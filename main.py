import requests
import json
import os

class Book:
    def __init__(self, id, title, authors, published_date, categories):
        self.id = id
        self.title = title
        self.authors = authors
        self.published_date = published_date
        self.categories = categories

    def __str__(self):
        return f"{self.title} by {', '.join(self.authors)}"

class BookClub:
    def __init__(self, name, members=None, books=None):
        self.name = name
        self.members = members or []
        self.books = books or []

    def add_member(self, member):
        if member not in self.members:
            self.members.append(member)

    def add_book(self, book):
        self.books.append(book)

class BookClubManager:
    def __init__(self, api_key):
        self.users = {}
        self.book_clubs = {}
        self.api_key = api_key

    def create_user_account(self, name, email, password):
        if email in self.users:
            return "User with email already exists"

        self.users[email] = {"name": name, "password": password, "book_ratings": {}}
        return "Account created successfully"

    def authenticate_user(self, email, password):
        if email in self.users:
            if self.users[email]["password"] == password:
                return True
        return False

    def search_books(self, query):
        url = f"https://www.googleapis.com/books/v1/volumes?q={query}&key={self.api_key}"

        try:
            response = requests.get(url)
            data = json.loads(response.text)
            books = []
            for item in data.get("items", []):
                book_info = item.get("volumeInfo", {})
                book_id = item.get("id")
                title = book_info.get("title")
                authors = book_info.get("authors", [])
                published_date = book_info.get("publishedDate")
                categories = book_info.get("categories", [])
                book = Book(book_id, title, authors, published_date, categories)
                books.append(book)
            return books
        except requests.exceptions.RequestException as e:
            raise Exception(f"An error occurred while retrieving book data: {e}")

    def get_book_details(self, book_id):
        url = f"https://www.googleapis.com/books/v1/volumes/{book_id}?key={self.api_key}"
        try:
            response = requests.get(url)
            data = json.loads(response.text)
            book_info = data.get("volumeInfo", {})
            book_id = data.get("id")
            title = book_info.get("title")
            authors = book_info.get("authors", [])
            published_date = book_info.get("publishedDate")
            categories = book_info.get("categories", [])
            return Book(book_id, title, authors, published_date, categories)
        except requests.exceptions.RequestException as e:
            raise Exception(f"An error occurred while retrieving book details: {e}")

    def create_book_club(self, user_email, name):
        if user_email not in self.users:
            return "User does not exist"

        book_club_id = len(self.book_clubs) + 1
        book_club = BookClub(name)
        book_club.add_member(user_email)
        self.book_clubs[book_club_id] = book_club

        return "Book club created successfully"

    def join_book_club(self, user_email, book_club_id):
        if user_email not in self.users:
            return "User does not exist"

        if book_club_id not in self.book_clubs:
            return "Book club does not exist"

        self.book_clubs[book_club_id].add_member(user_email)
        return "Joined book club successfully"

    def suggest_book(self, user_email, book_club_id, book_id):
        if user_email not in self.users:
            return "User does not exist"

        if book_club_id not in self.book_clubs:
            return "Book club does not exist"

        if user_email not in self.book_clubs[book_club_id].members:
            return "User is not a member of the book club"

        book_details = self.get_book_details(book_id)
        if book_details:
            self.book_clubs[book_club_id].add_book(book_details)
            return "Book suggestion added successfully"
        else:
            return "Failed to retrieve book details"


if __name__ == "__main__":
    google_books_api_key = os.getenv("GOOGLE_BOOKS_API_KEY")
    if not google_books_api_key:
        raise ValueError("Google Books API key is missing.")

    manager = BookClubManager(google_books_api_key)
    print(manager.create_user_account("John Doe", "johndoe@example.com", "password"))
    print(manager.authenticate_user("johndoe@example.com", "password"))
    print(manager.search_books("fiction"))
    print(manager.create_book_club("johndoe@example.com", "Book Club 1"))
    print(manager.join_book_club("johndoe@example.com", 1))
    print(manager.suggest_book("johndoe@example.com", 1, "book_id"))