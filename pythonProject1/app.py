ffrom flask import Flask, render_template, request
import pickle
import numpy as np
from pathlib import Path
from urllib.parse import urlparse

# --------------------------------------------------
# Flask Application
# --------------------------------------------------

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent


# --------------------------------------------------
# Load Data
# --------------------------------------------------

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


# --------------------------------------------------
# Image Helper Functions
# --------------------------------------------------

def clean_image_url(url):
    """
    Convert HTTP image URLs to HTTPS.
    This is important because Render uses HTTPS.
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

    # Make HTTP images HTTPS
    if url.startswith("http://"):
        url = "https://" + url[7:]

    # Validate URL
    parsed = urlparse(url)

    if parsed.scheme not in ["http", "https"]:
        return None

    if not parsed.netloc:
        return None

    return url


def get_image_column(df):
    """
    Prefer large images for better quality.
    """

    if "Image-URL-L" in df.columns:
        return "Image-URL-L"

    if "Image-URL-M" in df.columns:
        return "Image-URL-M"

    if "Image-URL-S" in df.columns:
        return "Image-URL-S"

    return None


# --------------------------------------------------
# Clean Popular Books
# --------------------------------------------------

POPULAR_IMAGE_COLUMN = get_image_column(popular_df)

if POPULAR_IMAGE_COLUMN:

    popular_df["clean_image"] = (
        popular_df[POPULAR_IMAGE_COLUMN]
        .apply(clean_image_url)
    )

    # Remove books without valid images
    popular_df = popular_df[
        popular_df["clean_image"].notna()
    ].copy()

else:

    popular_df["clean_image"] = None


# --------------------------------------------------
# Clean Books Dataset
# --------------------------------------------------

BOOK_IMAGE_COLUMN = get_image_column(books)

if BOOK_IMAGE_COLUMN:

    books["clean_image"] = (
        books[BOOK_IMAGE_COLUMN]
        .apply(clean_image_url)
    )

    # Remove books without valid images
    books = books[
        books["clean_image"].notna()
    ].copy()

else:

    books["clean_image"] = None


# --------------------------------------------------
# Home Page
# --------------------------------------------------

@app.route("/")
def index():

    return render_template(
        "index.html",

        book_name=popular_df[
            "Book-Title"
        ].tolist(),

        author=popular_df[
            "Book-Author"
        ].tolist(),

        image=popular_df[
            "clean_image"
        ].tolist(),

        votes=popular_df[
            "num_ratings"
        ].tolist(),

        rating=popular_df[
            "avg_rating"
        ].tolist()
    )


# --------------------------------------------------
# Recommendation Page
# --------------------------------------------------

@app.route("/recommend")
def recommend_ui():

    return render_template(
        "recommend.html"
    )


# --------------------------------------------------
# Recommendation Algorithm
# --------------------------------------------------

@app.route("/recommend_books", methods=["POST"])
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
            message="Please enter a book name!"
        )


    # --------------------------------------------------
    # Find Matching Book
    # --------------------------------------------------

    match = None

    for book in pt.index:

        if user_input in book.lower():

            match = book
            break


    # Book not found
    if match is None:

        return render_template(
            "recommend.html",
            data=[],
            message="Book not found! Please try another book."
        )


    # --------------------------------------------------
    # Find Similar Books
    # --------------------------------------------------

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


    # --------------------------------------------------
    # Prepare Recommendations
    # --------------------------------------------------

    data = []


    for i in similar_items[1:]:

        recommended_title = pt.index[i[0]]


        temp_df = books[
            books["Book-Title"] == recommended_title
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


        # Skip invalid images
        if not image_url:
            continue


        item = [

            row["Book-Title"],

            row["Book-Author"],

            image_url

        ]


        data.append(item)


        # Only 4 valid recommendations
        if len(data) == 4:
            break


    # --------------------------------------------------
    # No Valid Recommendations
    # --------------------------------------------------

    if not data:

        return render_template(
            "recommend.html",
            data=[],
            message="No recommendations with available book covers were found."
        )


    return render_template(
        "recommend.html",
        data=data
    )


# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.route("/health")
def health():

    return "Book Recommender is running successfully!"


# --------------------------------------------------
# Run Locally
# --------------------------------------------------

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
