import os
import requests

from flask import Flask, render_template, request
from flask_session import Session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from dotenv import load_dotenv

app = Flask(__name__)

# Load dotenv
load_dotenv('.env')

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/book/<string:isbn>")
def book(isbn):
    query = text("SELECT isbn, title, authors.author, year FROM books JOIN \
                 authors ON books.author = authors.author_id WHERE isbn = :isbn")  # noqa: E501
    book = db.execute(query, {"isbn": isbn}).fetchall()
    url = f"https://www.goodreads.com/book/review_counts.json?isbns={isbn}&key=\
            {os.getenv('API_KEY')}"
    res = requests.get(url)
    data = res.json()
    rating = data["books"][0]["average_rating"]
    return render_template("book.html", book=book, rating=rating)


@app.route("/search", methods=["POST"])
def search():
    search_keys = {"book": "title", "author": "authors.author", "isbn": "isbn"}
    search_for = f"%{request.form.get('searchfor').lower()}%"
    search_by = request.form.get("searchby").lower()
    try:
        search_by = search_keys[search_by]
    except KeyError:
        return "An error has occurred"
    query = text(f"SELECT isbn, title, authors.author, year FROM books JOIN \
                 authors ON books.author = authors.author_id WHERE LOWER \
                 ({search_by}) LIKE :search_for")
    books = db.execute(query, {"search_for": search_for}).fetchall()
    return render_template("search.html", books=books)
