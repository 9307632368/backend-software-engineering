"""Lesson 01: HTTP request methods, URL paths and query strings."""
from fastapi import FastAPI, HTTPException, Query, Response, status

app = FastAPI(title="Book Finder | HTTP and Routing")

BOOKS = {
    1: {"id": 1, "title": "Designing Data-Intensive Applications", "category": "systems"},
    2: {"id": 2, "title": "Deep Learning with Python", "category": "machine-learning"},
    3: {"id": 3, "title": "Clean Architecture", "category": "systems"},
}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/books")
def list_books(category: str | None = None, search: str | None = Query(default=None, min_length=2)):
    books = list(BOOKS.values())
    if category:
        books = [book for book in books if book["category"] == category]
    if search:
        books = [book for book in books if search.casefold() in book["title"].casefold()]
    return {"count": len(books), "items": books}


@app.get("/books/{book_id}")
def read_book(book_id: int, response: Response):
    book = BOOKS.get(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    response.headers["X-Lesson"] = "routing"
    return book


@app.post("/echo", status_code=status.HTTP_201_CREATED)
def echo(message: str = Query(min_length=1)):
    return {"received": message}
