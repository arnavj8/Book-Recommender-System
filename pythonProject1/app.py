from flask import Flask, render_template, request
import pickle
import numpy as np
from pathlib import Path
from urllib.parse import urlparse
import re

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent

# ---------------------------------------------------------
# Load preprocessed data
# ---------------------------------------------------------
popular_df = pickle.load(open(BASE_DIR / "popular.pkl", "rb"))
pt = pickle.load(open(BASE_DIR / "pt.pkl", "rb"))
books = pickle.load(open(BASE_DIR / "books.pkl", "rb"))
similarity_scores = pickle.load(open(BASE_DIR / "similarity_scores.pkl", "rb"))


# ---------------------------------------------------------
# Image helpers
# ---------------------------------------------------------
def clean_image_url(url):
    """Return a usable HTTPS image URL or None."""
    if url is None:
        return None

    url = str(url).strip()

    if not url or url.lower() in {"nan", "none", "null"}:
        return None

    invalid_words = (
        "nopic",
        "no_image",
        "no-image",
        "noimage",
        "placeholder",
        "default-image",
        "default_image",
    )

    lower_url = url.lower()
    if any(word in lower_url for word in invalid_words):
        return None

    if url.startswith("http://"):
        url = "https://" + url[7:]

    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None

    return url


def normalize_isbn(isbn):
    """Keep only ISBN digits and X."""
    if isbn is None:
        return None

    value = re.sub(r"[^0-9Xx]", "", str(isbn)).upper()

    if len(value) in (10, 13):
        return value

    return None


def dataset_image(row):
    """Use the largest available image from the Book-Crossing data."""
    for column in ("Image-URL-L", "Image-URL-M", "Image-URL-S"):
        if column in row.index:
            image = clean_image_url(row[column])
            if image:
                return image

    return None


def openlibrary_image(row):
    """
    Prefer Open Library's large cover when an ISBN is available.
    Open Library documents S/M/L cover sizes and supports ISBN-based
    cover URLs.
    """
    if "ISBN" not in row.index:
        return None

    isbn = normalize_isbn(row["ISBN"])

    if not isbn:
        return None

    return f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg?default=false"


def get_image_pair(row):
    """
    Return (primary, fallback).

    Primary: Open Library large cover when ISBN exists.
    Fallback: original Book-Crossing large/medium/small URL.
    """
    fallback = dataset_image(row)
    primary = openlibrary_image(row)

    if primary:
        return primary, fallback

    if fallback:
        return fallback, None

    return None, None


# ---------------------------------------------------------
# Build a fast title -> image lookup from books.pkl
# ---------------------------------------------------------
books = books.copy()

book_image_lookup = {}

for _, row in books.iterrows():
    title = row.get("Book-Title")

    if not title or str(title).strip() == "":
        continue

    primary, fallback = get_image_pair(row)

    if primary:
        # Keep the first valid cover found for a title.
        book_image_lookup.setdefault(
            str(title),
            (primary, fallback)
        )


def get_best_image(title):
    return book_image_lookup.get(str(title))


# ---------------------------------------------------------
# Home page
# ---------------------------------------------------------
@app.route("/")
def index():
    book_name = []
    author = []
    images = []
    votes = []
    rating = []

    # Keep the popular-book ordering from popular.pkl.
    for _, row in popular_df.iterrows():
        title = row["Book-Title"]
        image_pair = get_best_image(title)

        # Do not display books for which we have no cover.
        if not image_pair:
            continue

        book_name.append(title)
        author.append(row["Book-Author"])
        images.append(image_pair)
        votes.append(row["num_ratings"])
        rating.append(row["avg_rating"])

    return render_template(
        "index.html",
        book_name=book_name,
        author=author,
        images=images,
        votes=votes,
        rating=rating,
    )


# ---------------------------------------------------------
# Recommendation page
# ---------------------------------------------------------
@app.route("/recommend")
def recommend_ui():
    return render_template("recommend.html")


# ---------------------------------------------------------
# Recommendation endpoint
# ---------------------------------------------------------
@app.route("/recommend_books", methods=["POST"])
def recommend():
    user_input = request.form.get("user_input", "").strip().lower()

    if not user_input:
        return render_template(
            "recommend.html",
            data=[],
            message="Please enter a book name!",
        )

    match = None

    for book in pt.index:
        if user_input in str(book).lower():
            match = book
            break

    if match is None:
        return render_template(
            "recommend.html",
            data=[],
            message="Book not found! Please try another book name.",
        )

    index = np.where(pt.index == match)[0][0]

    similar_items = sorted(
        enumerate(similarity_scores[index]),
        key=lambda x: x[1],
        reverse=True,
    )

    data = []

    for item_index, _score in similar_items[1:]:
        recommended_title = pt.index[item_index]
        image_pair = get_best_image(recommended_title)

        # Skip books without a usable cover.
        if not image_pair:
            continue

        temp_df = books[
            books["Book-Title"] == recommended_title
        ].drop_duplicates("Book-Title")

        if temp_df.empty:
            continue

        row = temp_df.iloc[0]

        data.append(
            [
                row["Book-Title"],
                row["Book-Author"],
                image_pair[0],  # primary
                image_pair[1],  # fallback
            ]
        )

        if len(data) == 4:
            break

    if not data:
        return render_template(
            "recommend.html",
            data=[],
            message="No recommendations with available book covers were found.",
        )

    return render_template("recommend.html", data=data)


# ---------------------------------------------------------
# Health check
# ---------------------------------------------------------
@app.route("/health")
def health():
    return "Book Recommender is running successfully!"


# ---------------------------------------------------------
# Local development
# ---------------------------------------------------------
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )
