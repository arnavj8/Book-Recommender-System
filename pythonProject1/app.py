from flask import Flask, render_template, request
import pickle
import numpy as np
from pathlib import Path

# --------------------------------------------------
# Flask Application
# --------------------------------------------------

app = Flask(__name__)

# Directory containing app.py
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
# Home Page
# --------------------------------------------------

@app.route("/")
def index():

    # Use large book cover images when available
    if "Image-URL-L" in popular_df.columns:
        image_column = "Image-URL-L"
    else:
        image_column = "Image-URL-M"

    return render_template(
        "index.html",

        book_name=popular_df["Book-Title"].tolist(),

        author=popular_df["Book-Author"].tolist(),

        image=popular_df[image_column].tolist(),

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

    # Get user input safely
    user_input = request.form.get(
        "user_input",
        ""
    ).strip().lower()

    # Check empty input
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
    )[1:5]


    # --------------------------------------------------
    # Prepare Recommendation Data
    # --------------------------------------------------

    data = []

    for i in similar_items:

        item = []

        recommended_title = pt.index[i[0]]

        temp_df = books[
            books["Book-Title"] == recommended_title
        ]

        temp_df = temp_df.drop_duplicates(
            "Book-Title"
        )

        # Book title
        item.extend(
            temp_df["Book-Title"].tolist()
        )

        # Author
        item.extend(
            temp_df["Book-Author"].tolist()
        )

        # Use large image if available
        if "Image-URL-L" in temp_df.columns:

            item.extend(
                temp_df["Image-URL-L"].tolist()
            )

        else:

            item.extend(
                temp_df["Image-URL-M"].tolist()
            )

        data.append(item)


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
# Run Application Locally
# --------------------------------------------------

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
