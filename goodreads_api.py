import os
import requests


def retrieve_data(isbn):
    url = f"https://www.goodreads.com/book/review_counts.json?isbns={isbn}&key=\
            {os.getenv('API_KEY')}"
    res = requests.get(url)

    # Make sure book exists in Goodreads db
    if res.status_code != 200:
        return None
    else:
        data = res.json()
        return data
