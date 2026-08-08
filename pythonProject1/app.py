from flask import Flask, render_template, request
import pickle
import numpy as np
from pathlib import Path

# --------------------------------------------------
# Flask App
# --------------------------------------------------

app = Flask(__name__)

# Get the directory where app.py is located
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
    return render_template(
        "index.html",
        book_name=popular_df["Book-Title"].tolist(),
        author=popular_df["Book-Author"].tolist(),
        image=popular_df["Image-URL-M"].tolist(),
        votes=popular_df["num_ratings"].tolist(),
        rating=popular_df["avg_rating"].tolist()
    )


# --------------------------------------------------
# Recommendation Page
# --------------------------------------------------

@app.route("/recommend")
def recommend_ui():
    return render_template("recommend.html")


# --------------------------------------------------
# Book Recommendation
# --------------------------------------------------

@app.route("/recommend_books", methods=["POST"])
def recommend():

    user_input = request.form.get("user_input", "").strip().lower()

    # Check empty input
    if not user_input:
        return render_template(
            "recommend.html",
            data=[],
            message="Please enter a book name!"
        )

    # Find a matching book
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
            message="Book not found!"
        )

    # Find index of matched book
    index = np.where(pt.index == match)[0][0]

    # Find similar books
    similar_items = sorted(
        list(enumerate(similarity_scores[index])),
        key=lambda x: x[1],
        reverse=True
    )[1:5]

    # Store recommendation data
    data = []

    for i in similar_items:

        item = []

        temp_df = books[
            books["Book-Title"] == pt.index[i[0]]
        ]

        temp_df = temp_df.drop_duplicates("Book-Title")

        item.extend(temp_df["Book-Title"].tolist())
        item.extend(temp_df["Book-Author"].tolist())
        item.extend(temp_df["Image-URL-M"].tolist())

        data.append(item)

    return render_template(
        "recommend.html",
        data=data
    )


# --------------------------------------------------
# Local Development
# --------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)