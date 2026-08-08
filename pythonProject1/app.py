from flask import Flask, render_template, request
import pickle
import numpy as np
from pathlib import Path

# --------------------------------------------------
# Flask Application
# --------------------------------------------------

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent


# --------------------------------------------------
# Load Preprocessed Data
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
# Select Best Image Column
# --------------------------------------------------

if "Image-URL-L" in popular_df.columns:
    POPULAR_IMAGE_COLUMN = "Image-URL-L"
else:
    POPULAR_IMAGE_COLUMN = "Image-URL-M"


if "Image-URL-L" in books.columns:
    BOOK_IMAGE_COLUMN = "Image-URL-L"
else:
    BOOK_IMAGE_COLUMN = "Image-URL-M"


# --------------------------------------------------
# Remove Books Without Images
# --------------------------------------------------

popular_df = popular_df[
    popular_df[POPULAR_IMAGE_COLUMN].notna()
]

popular_df = popular_df[
    popular_df[POPULAR_IMAGE_COLUMN].astype(str).str.strip() != ""
]


books = books[
    books[BOOK_IMAGE_COLUMN].notna()
]

books = books[
    books[BOOK_IMAGE_COLUMN].astype(str).str.strip() != ""
]


# --------------------------------------------------
# Home Page
# --------------------------------------------------

@app.route("/")
def index():

    return render_template(
        "index.html",

        book_name=popular_df["Book-Title"].tolist(),

        author=popular_df["Book-Author"].tolist(),

        image=popular_df[POPULAR_IMAGE_COLUMN].tolist(),

        votes=popular_df["num_ratings"].tolist(),

        rating=popular_df["avg_rating"].tolist()
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
# Book Recommendation
# --------------------------------------------------

@app.route("/recommend_books", methods=["POST"])
def recommend():

    user_input = request.form.get(
        "user_input",
        ""
    ).strip().lower()

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


    if match is None:

        return render_template(
            "recommend.html",
            data=[],
            message="Book not found! Please try another book name."
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

        temp_df = temp_df.drop_duplicates(
            "Book-Title"
        )


        if temp_df.empty:
            continue


        # Get image
        image_url = temp_df.iloc[0][BOOK_IMAGE_COLUMN]


        # Skip books without an image
        if (
            image_url is None
            or str(image_url).strip() == ""
            or str(image_url).lower() == "nan"
        ):
            continue


        item = [

            temp_df.iloc[0]["Book-Title"],

            temp_df.iloc[0]["Book-Author"],

            image_url

        ]

        data.append(item)


        # We only need 4 books with valid images
        if len(data) == 4:
            break


    # --------------------------------------------------
    # No Recommendations Found
    # --------------------------------------------------

    if not data:

        return render_template(
            "recommend.html",
            data=[],
            message="Sorry, no books with available images were found."
        )


    # --------------------------------------------------
    # Display Recommendations
    # --------------------------------------------------

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
