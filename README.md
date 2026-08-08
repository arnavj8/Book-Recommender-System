# 📚 BookVerse — Book Recommendation System

**BookVerse** is a Flask-based web application that helps users discover books through a **Collaborative Filtering-based recommendation system**.

The application uses preprocessed book data and similarity scores to recommend books similar to the one selected by the user. BookVerse is designed with a simple and responsive interface and is **deployed on Render** for online access.

## 🌐 Live Demo

🚀 **BookVerse:**
https://bookverse-6r4q.onrender.com/

> Note: Since the application is hosted on Render's free tier, the first request may take a few seconds if the service has been inactive.

## ✨ Features

* 📖 **Popular Books** — Displays popular books based on ratings and number of ratings.
* 🤖 **Book Recommendations** — Recommends similar books based on the selected book.
* 🔍 **Book Search** — Search for a book by entering its title.
* ⭐ **Ratings Information** — Displays average ratings and number of ratings.
* 🖼️ **Book Covers** — Displays book cover images from the available book data.
* ⚡ **Fast Recommendations** — Uses precomputed similarity scores instead of calculating them for every request.
* 🌐 **Flask Web Application** — Provides a lightweight and interactive web interface.
* ☁️ **Render Deployment** — The application is deployed and accessible online.

## 🧠 Recommendation System

BookVerse uses a **Collaborative Filtering approach** with precomputed similarity scores.

The recommendation process works as follows:

```text
User enters a book title
        ↓
Search for the matching book
        ↓
Find the book's index
        ↓
Retrieve precomputed similarity scores
        ↓
Sort books by similarity
        ↓
Select top similar books
        ↓
Display recommendations
```

The similarity scores are stored in:

```text
similarity_scores.pkl
```

This allows the Flask application to load the precomputed scores instead of performing the similarity calculation every time a user requests recommendations.

## 🛠️ Tech Stack

| Technology  | Purpose                                  |
| ----------- | ---------------------------------------- |
| 🐍 Python   | Core programming language                |
| 🌐 Flask    | Backend web framework                    |
| 📊 Pandas   | Data handling and DataFrame operations   |
| 🔢 NumPy    | Numerical operations                     |
| 📦 Pickle   | Loading preprocessed recommendation data |
| 🎨 HTML/CSS | Frontend interface                       |
| ☁️ Render   | Cloud deployment                         |

> **Note:** Scikit-learn is not directly used in the Flask application code. The application loads precomputed similarity scores from `similarity_scores.pkl`.

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
│   └── requirements.txt
│
├── .gitignore
├── README.md
└── LICENSE
```

### Important Files

| File                    | Description                        |
| ----------------------- | ---------------------------------- |
| `app.py`                | Main Flask application             |
| `popular.pkl`           | Preprocessed popular-book data     |
| `books.pkl`             | Book metadata                      |
| `pt.pkl`                | Processed book matrix              |
| `similarity_scores.pkl` | Precomputed book similarity scores |
| `index.html`            | Home page                          |
| `recommend.html`        | Recommendation page                |
| `requirements.txt`      | Python dependencies                |

## 🚀 Run Locally

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

### 4. Activate the Virtual Environment

**Windows:**

```bash
.venv\Scripts\activate
```

**macOS/Linux:**

```bash
source .venv/bin/activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Run Flask

```bash
python app.py
```

The application will be available at:

```text
http://127.0.0.1:5000
```

or:

```text
http://localhost:5000
```

## ☁️ Deployment on Render

BookVerse is deployed using **Render**.

The deployment process is:

```text
GitHub Repository
        ↓
      Render
        ↓
Install dependencies
        ↓
Start Flask application
        ↓
Live Web Application
```

### Render Configuration

A typical Render configuration for the project is:

**Build Command**

```bash
pip install -r requirements.txt
```

**Start Command**

```bash
gunicorn app:app
```

If the Render service uses `pythonProject1` as its root directory, the command can be configured according to that directory structure.

## 🔄 How Recommendations Work

When a user submits a book title:

1. The input is converted to lowercase.
2. BookVerse searches the processed book index for a matching title.
3. The corresponding index is retrieved.
4. Precomputed similarity scores are accessed.
5. Books are sorted according to their similarity score.
6. The top four similar books are selected.
7. Book title, author, and cover information are displayed.

If the entered book cannot be found, the application displays:

```text
Book not found!
```

If no book name is entered:

```text
Please enter a book name!
```

## 📊 Preprocessed Data

BookVerse uses preprocessed `.pkl` files to improve recommendation speed.

### `popular.pkl`

Contains information about popular books, including:

* Book title
* Author
* Number of ratings
* Average rating
* Book cover

### `books.pkl`

Contains book metadata used to retrieve information about recommended books.

### `pt.pkl`

Contains the processed book matrix used to locate books within the recommendation system.

### `similarity_scores.pkl`

Contains precomputed similarity scores used to identify books that are most similar to the selected book.

## 🔗 Application Routes

| Route              | Method | Description                            |
| ------------------ | ------ | -------------------------------------- |
| `/`                | GET    | Displays popular books                 |
| `/recommend`       | GET    | Opens the recommendation page          |
| `/recommend_books` | POST   | Processes book recommendation requests |

## 🎯 Project Objective

The objective of BookVerse is to provide users with a simple platform for discovering books based on their reading interests.

Instead of manually browsing through a large collection of books, users can enter a book they like and receive similar book recommendations.

## 🔮 Future Improvements

* 👤 User accounts and personalized recommendations
* ⭐ User ratings and reviews
* ❤️ Wishlist and favorite books
* 🔎 Advanced book search
* 📚 Genre-based recommendations
* 🧠 Hybrid recommendation system
* 🤖 AI-powered natural language recommendations
* 🗄️ Database integration
* 📈 Recommendation analytics
* 📱 Improved mobile responsiveness

## 📚 Learning Outcomes

This project provided practical experience in:

* Building recommendation systems
* Collaborative Filtering
* Similarity-based recommendations
* Data preprocessing
* Pandas and NumPy
* Pickle-based data serialization
* Flask web development
* HTML/CSS frontend development
* Deploying Python applications on Render
* Managing Python dependencies with `requirements.txt`
* Using Git and GitHub for version control

## 👨‍💻 Author

**Arnav Jain**

B.Tech — Artificial Intelligence & Data Science

GitHub:
https://github.com/arnavj8

## 📄 License

This project is licensed under the **MIT License**.

---

⭐ If you found BookVerse useful, consider giving the repository a star!
