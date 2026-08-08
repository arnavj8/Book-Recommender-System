from flask import Flask, render_template, request
import pickle
import numpy as np
from pathlib import Path
from urllib.parse import urlparse
import re

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent


# =========================================================
# LOAD DATA
# =========================================================

popular_df = pickle.load(
    open(BASE_DIR / "popular.pkl", "rb")
)

pt = pickle.load(
    open(BASE_DIR / "pt.pkl", "rb")
)

books = pickle.load(
    open(BASE_DIR / "books.pkl", "rb")
)

similarity_scores = pickle.load(
    open(BASE_DIR / "similarity_scores.pkl", "rb")
)


# =========================================================
# IMAGE FUNCTIONS
# =========================================================

def clean_image_url(url):
    """
    Clean and validate image URL.
    """

    if url is None:
        return None

    url = str(url).strip()

    if not url:
        return None

    if url.lower() in ["nan", "none", "null"]:
        return None

    invalid_words = [
        "nopic",
        "no_image",
        "no-image",
        "noimage",
        "placeholder",
        "default-image",
        "default_image"
    ]

    lower_url = url.lower()

    for word in invalid_words:
        if word in lower_url:
            return None

    # Convert HTTP to HTTPS
    if url.startswith("http://"):
        url = "https://" + url[7:]

    parsed = urlparse(url)

    if parsed.scheme not in ["http", "https"]:
        return None

    if not parsed.netloc:
        return None

    return url


def normalize_isbn(isbn):
    """
    Clean ISBN for Open Library cover lookup.
    """

    if isbn is None:
        return None

    isbn = re.sub(
        r"[^0-9Xx]",
        "",
        str(isbn)
    ).upper()

    if len(isbn) in [10, 13]:
        return isbn

    return None


def get_dataset_image(row):
    """
    Get the largest available image from books.pkl.
    """

    image_columns = [
        "Image-URL-L",
        "Image-URL-M",
        "Image-URL-S"
    ]

    for column in image_columns:

        if column in row.index:

            image = clean_image_url(
                row[column]
            )

            if image:
                return image

    return None


def get_openlibrary_image(row):
    """
    Generate a large Open Library cover URL
    using ISBN.
    """

    if "ISBN" not in row.index:
        return None

    isbn = normalize_isbn(
        row["ISBN"]
    )

    if not isbn:
        return None

    return (
        f"https://covers.openlibrary.org/"
        f"b/isbn/{isbn}-L.jpg?default=false"
    )


def get_image_pair(row):
    """
    Return:

    [primary_image, fallback_image]
    """

    dataset_image = get_dataset_image(row)

    openlibrary_image = get_openlibrary_image(row)

    if openlibrary_image:

        return [
            openlibrary_image,
            dataset_image
        ]

    if dataset_image:

        return [
            dataset_image,
            None
        ]

    return None


# =========================================================
# CREATE IMAGE LOOKUP
# =========================================================

book_image_lookup = {}


for _, row in books.iterrows():

    title = row.get("Book-Title")

    if title is None:
        continue

    title = str(title).strip()

    if not title:
        continue

    image_pair = get_image_pair(row)

    if image_pair:

        if title not in book_image_lookup:

            book_image_lookup[title] = image_pair


def get_best_image(title):

    if title is None:
        return None

    return book_image_lookup.get(
        str(title)
    )


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def index():

    book_name = []
    author = []
    image = []
    votes = []
    rating = []


    for _, row in popular_df.iterrows():

        title = row["Book-Title"]

        image_pair = get_best_image(
            title
        )


        # Skip books without images
        if not image_pair:
            continue


        book_name.append(
            title
        )

        author.append(
            row["Book-Author"]
        )

        image.append(
            image_pair
        )

        votes.append(
            row["num_ratings"]
        )

        rating.append(
            row["avg_rating"]
        )


    return render_template(

        "index.html",

        book_name=book_name,

        author=author,

        image=image,

        votes=votes,

        rating=rating
    )


# =========================================================
# RECOMMEND PAGE
# =========================================================

@app.route("/recommend")
def recommend_ui():

    return render_template(
        "recommend.html"
    )


# =========================================================
# RECOMMEND BOOKS
# =========================================================

@app.route(
    "/recommend_books",
    methods=["POST"]
)
def recommend():

    user_input = request.form.get(
        "user_input",
        ""
    ).strip().lower()


    # Empty input
    if not user_input:

        return render_template(
            "recommend.html",

            data=[],

            message=(
                "Please enter a book name!"
            )
        )


    # =====================================================
    # FIND BOOK
    # =====================================================

    match = None


    for book in pt.index:

        if user_input in str(
            book
        ).lower():

            match = book

            break


    # Book not found
    if match is None:

        return render_template(

            "recommend.html",

            data=[],

            message=(
                "Book not found! "
                "Please try another book name."
            )
        )


    # =====================================================
    # FIND SIMILAR BOOKS
    # =====================================================

    index = np.where(
        pt.index == match
    )[0][0]


    similar_items = sorted(

        enumerate(
            similarity_scores[index]
        ),

        key=lambda x: x[1],

        reverse=True
    )


    data = []


    # =====================================================
    # GET 4 RECOMMENDATIONS WITH IMAGES
    # =====================================================

    for item_index, score in similar_items[1:]:

        recommended_title = pt.index[
            item_index
        ]


        image_pair = get_best_image(
            recommended_title
        )


        # Skip books without image
        if not image_pair:
            continue


        temp_df = books[
            books["Book-Title"] ==
            recommended_title
        ]


        if temp_df.empty:
            continue


        temp_df = temp_df.drop_duplicates(
            "Book-Title"
        )


        if temp_df.empty:
            continue


        row = temp_df.iloc[0]


        data.append([

            row["Book-Title"],

            row["Book-Author"],

            image_pair[0],

            image_pair[1]

        ])


        if len(data) == 4:
            break


    # =====================================================
    # NO RESULTS
    # =====================================================

    if not data:

        return render_template(

            "recommend.html",

            data=[],

            message=(
                "No recommendations with "
                "available book covers were found."
            )
        )


    # =====================================================
    # SHOW RESULTS
    # =====================================================

    return render_template(

        "recommend.html",

        data=data
    )


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/health")
def health():

    return (
        "Book Recommender is running successfully!"
    )


# =========================================================
# RUN LOCALLY
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
