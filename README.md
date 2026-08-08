# 📚 BookVerse — Book Recommendation System

BookVerse is a **web-based book recommendation system** built with **Python and Flask** that helps users discover books based on their interests.

The system uses **Collaborative Filtering** to identify books similar to a user's selected book and provides personalized recommendations along with book covers and author information.

## ✨ Features

* 📖 **Popular Books** — Displays highly rated and frequently reviewed books.
* 🤖 **Personalized Recommendations** — Recommends books similar to the book selected by the user.
* 🔍 **Book Search** — Users can enter a book title to find recommendations.
* ⭐ **Ratings & Reviews** — Displays average ratings and number of ratings for popular books.
* 🖼️ **Book Cover Integration** — Uses available dataset images with Open Library as a fallback for missing covers.
* ⚡ **Fast Recommendations** — Precomputed similarity scores are used for efficient recommendations.
* 🌐 **Simple Web Interface** — Clean and responsive Flask-based interface.
* ❤️ **Reader-Friendly Experience** — Designed to make discovering new books simple and intuitive.

## 🧠 Recommendation System

BookVerse uses a **Collaborative Filtering** approach.

The recommendation pipeline works as follows:

```text
User selects a book
        ↓
Find matching book in dataset
        ↓
Retrieve similarity scores
        ↓
Rank similar books
        ↓
Select top recommendations
        ↓
Display book title, author & cover
```

The project stores preprocessed recommendation data and similarity matrices using Python pickle files, allowing recommendations to be generated without retraining the model every time the application starts.

## 🛠️ Tech Stack

| Technology      | Purpose                                              |
| --------------- | ---------------------------------------------------- |
| 🐍 Python       | Core programming language                            |
| 🌐 Flask        | Web application framework                            |
| 📊 Pandas       | Data manipulation                                    |
| 🔢 NumPy        | Numerical computations                               |
| 🤖 Scikit-learn | Recommendation/modeling utilities                    |
| 🎨 HTML/CSS     | Frontend interface                                   |
| 📦 Pickle       | Storing processed datasets and recommendation models |
| 📚 Open Library | Book-cover fallback                                  |

The current repository includes Flask, NumPy, Pandas, Gunicorn, and Scikit-learn as its main Python dependencies.

## 📁 Project Structure

```text
BookVerse/
│
├── pythonProject1/
│   ├── templates/
│   │   ├── index.html
│   │   └── recommend.html
│   │
│   ├── app.py
│   ├── books.pkl
│   ├── popular.pkl
│   ├── pt.pkl
│   ├── similarity_scores.pkl
│   ├── requirements.txt
│   └── __init__.py
│
├── .gitignore
├── .gitattributes
├── .python-version
└── LICENSE
```

The recommendation data files include `books.pkl`, `popular.pkl`, `pt.pkl`, and `similarity_scores.pkl`.

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/arnavj8/BookVerse.git
```

### 2. Navigate to the Project

```bash
cd BookVerse/pythonProject1
```

### 3. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

For macOS/Linux:

```bash
source .venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Application

```bash
python app.py
```

The Flask application runs on:

```text
http://localhost:5000
```

## 📖 How It Works

### Popular Books

The home page loads preprocessed popular-book data and displays information such as:

* Book title
* Author
* Average rating
* Number of ratings
* Book cover

The application filters out books for which no usable cover image is available.

### Book Recommendations

When a user enters a book title:

1. BookVerse searches for the matching title.
2. The corresponding position in the recommendation matrix is identified.
3. Similarity scores are retrieved.
4. Books are sorted according to similarity.
5. The top four books with available covers are selected.
6. Recommended books are displayed with their title, author, and cover.

### 🖼️ Image Handling

BookVerse uses a two-level image strategy:

```text
Book ISBN
   ↓
Open Library Cover
   ↓
If unavailable
   ↓
Dataset Cover
```

The application validates image URLs, converts HTTP URLs to HTTPS, removes invalid/placeholder images, and generates Open Library cover URLs using ISBNs.

## 📊 Dataset

The project uses book information containing attributes such as:

* Book title
* Book author
* ISBN
* Book cover URLs
* Rating information

The processed datasets and recommendation artifacts are stored as `.pkl` files and loaded when the Flask application starts.

## 🔗 Application Routes

| Route              | Description                            |
| ------------------ | -------------------------------------- |
| `/`                | Home page with popular books           |
| `/recommend`       | Recommendation interface               |
| `/recommend_books` | Processes book recommendation requests |
| `/health`          | Application health check               |

## 🎯 Project Objective

The main objective of BookVerse is to build an intelligent recommendation platform that helps users discover books they are likely to enjoy without manually browsing through thousands of titles.

By combining **machine learning, similarity-based recommendations, and a web interface**, BookVerse provides a simple and interactive book-discovery experience.

## 🔮 Future Improvements

* 👤 User authentication and personalized profiles
* ⭐ User rating and review system
* 🧠 Hybrid recommendation system
* 🔎 Advanced search and filtering
* 📚 Genre-based recommendations
* ❤️ Wishlist and favorites
* 📈 Recommendation analytics
* ☁️ Cloud deployment
* 🗄️ Database integration instead of local pickle files
* 🤖 AI-powered natural-language book recommendations

## 💡 Learning Outcomes

Through this project, I gained practical experience in:

* Building recommendation systems
* Collaborative Filtering
* Similarity-based recommendation
* Data preprocessing with Pandas
* Model/data serialization using Pickle
* Flask web development
* Integrating external image sources
* Designing a machine-learning-powered web application
* Deploying Python applications using production-ready tools such as Gunicorn

## 👨‍💻 Author

**Arnav Jain**

B.Tech — Artificial Intelligence & Data Science

GitHub: [arnavj8](https://github.com/arnavj8)

## 📄 License

This project is licensed under the **MIT License**.

---

⭐ If you found this project useful, consider giving the repository a star!

