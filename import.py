import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from dotenv import load_dotenv

# Load dotenv
load_dotenv('.env')

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def list_authors():
    """Extract and sort all unique authors from file."""
    with open("books.csv") as f:
        data_list = list(csv.reader(f))
        authors = []
        for row in data_list[1:]:
            authors.append(row[2])

        # Remove duplicates and sort by last name
        authors = set(list(authors))
        authors = sorted(authors)

        # Pregenerate authors table with id as key
        authors_table = {}
        for author in authors:
            authors_table[authors.index(author)+1] = author

        return authors_table


def create_authors():
    """Create authors table and insert rows."""
    authors = list_authors()
    count = 1
    total = len(authors)

    # Create table
    db.execute("CREATE TABLE authors (\
                author_id SERIAL PRIMARY KEY,\
                author VARCHAR NOT NULL\
                )")

    # Insert rows
    for author_id in authors:
        db.execute("INSERT INTO authors VALUES (:author_id, :author)",
                   {"author_id": author_id, "author": authors[author_id]})
        total = len(authors)
        print(f"Added {count}/{total}")
        count += 1

    db.commit()


def create_books():
    """Create books table and insert rows."""
    authors = list_authors()

    # Create table
    db.execute("CREATE TABLE books (\
                book_id SERIAL PRIMARY KEY,\
                isbn VARCHAR NOT NULL,\
                title VARCHAR NOT NULL,\
                author INTEGER REFERENCES authors,\
                year INTEGER NOT NULL\
                )")

    # Insert rows
    with open("books.csv") as f:
        data_list = list(csv.reader(f))
        book_id = 1
        count = 1
        total = len(data_list) - 1
        for isbn, title, author, year in data_list[1:]:
            author = list(authors.values()).index(author) + 1
            db.execute("INSERT INTO books VALUES (:book_id, :isbn, :title,\
                                                  :author, :year)",
                       {"book_id": book_id, "isbn": isbn, "title": title,
                        "author": author, "year": year})

            print(f"Added book {book_id} ({count}/{total})")
            book_id += 1
            count += 1

    db.commit()


def main():
    create_authors()
    create_books()


if __name__ == "__main__":
    main()
