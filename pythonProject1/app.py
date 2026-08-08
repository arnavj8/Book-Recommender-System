from flask import Flask, render_template, request
import pickle
import numpy as np
from pathlib import Path
from urllib.parse import urlparse


# =========================================================
# Flask Application
# =========================================================

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent


# =========================================================
# Load Pickle Files
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

def get_image_column(df):
    """
    Select the highest-quality image column available.
    """

    if "Image-URL-L" in df.columns:
        return "Image-URL-L"

    if "Image-URL-M" in df.columns:
        return "Image-URL-M"

    if "Image-URL-S" in df.columns:
        return "Image-URL-S"

    return None


def clean_image_url(url):
    """
    Validate and clean book image URLs.
    """

    if url is None:
        return None

    url = str(url).strip()

    if not url:
        return None

    if url.lower() in ["nan", "none", "null"]:
        return None

    # Remove common placeholder images
    invalid_words = [
        "nopic",
        "no_image",
        "no-image",
        "noimage",
        "placeholder",
        "default-image",
        "default_image"
    ]

    url_lower = url.lower()

    for word in invalid_words:
        if word in url_lower:
            return None

    # Convert HTTP → HTTPS
    if url.startswith("http://"):
        url = "https://" + url[7:]

    # Validate URL
    parsed = urlparse(url)

    if parsed.scheme not in ["http", "https"]:
        return None

    if not parsed.netloc:
        return None

    return url


# =========================================================
# IMAGE COLUMN FOR BOOK DATASET
# =========================================================

BOOK_IMAGE_COLUMN = get_image_column(books)

if BOOK_IMAGE_COLUMN:

    books["clean_image"] = (
        books[BOOK_IMAGE_COLUMN]
        .apply(clean_image_url)
    )

else:

    books["clean_image"] = None


# =========================================================
# REMOVE BOOKS WITHOUT VALID IMAGES
# =========================================================

books = books[
    books["clean_image"].notna()
].copy()


# =========================================================
# CREATE BOOK IMAGE LOOKUP
# =========================================================

def get_best_image(title):
    """
    Get the best available image for a book.

    Images are always taken from books.pkl so that
    homepage and recommendation page use the same
    image source.
    """

    temp_df = books[
        books["Book-Title"] == title
    ]

    if temp_df.empty:
        return None

    for _, row in temp_df.iterrows():

        image = row["clean_image"]

        if image:
            return image

    return None


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

        # Get image from books.pkl
        best_image = get_best_image(title)

        # Skip books without valid images
        if not best_image:
            continue

        book_name.append(title)

        author.append(
            row["Book-Author"]
        )

        image.append(
            best_image
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
# RECOMMENDATION PAGE
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


    # -----------------------------------------------------
    # Empty Input
    # -----------------------------------------------------

    if not user_input:

        return render_template(
            "recommend.html",
            data=[],
            message="Please enter a book name!"
        )


    # -----------------------------------------------------
    # Find Matching Book
    # -----------------------------------------------------

    match = None

    for book in pt.index:

        if user_input in book.lower():

            match = book
            break


    # -----------------------------------------------------
    # Book Not Found
    # -----------------------------------------------------

    if match is None:

        return render_template(
            "recommend.html",
            data=[],
            message=(
                "Book not found! "
                "Please try another book name."
            )
        )


    # -----------------------------------------------------
    # Find Similar Books
    # -----------------------------------------------------

    index = np.where(
        pt.index == match
    )[0][0]


    similar_items = sorted(
        list(
            enumerate(
                similarity_scores[index]
            )
        ),
        key=lambda x: x[1],
        reverse=True
    )


    # -----------------------------------------------------
    # Prepare Recommendations
    # -----------------------------------------------------

    data = []


    for i in similar_items[1:]:

        recommended_title = pt.index[i[0]]


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


        image_url = row["clean_image"]


        # Skip invalid image
        if not image_url:
            continue


        data.append(
            [
                row["Book-Title"],
                row["Book-Author"],
                image_url
            ]
        )


        # Return only 4 valid books
        if len(data) == 4:
            break


    # -----------------------------------------------------
    # No Recommendations
    # -----------------------------------------------------

    if not data:

        return render_template(
            "recommend.html",
            data=[],
            message=(
                "No recommendations with "
                "available book covers were found."
            )
        )


    # -----------------------------------------------------
    # Render Results
    # -----------------------------------------------------

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
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
