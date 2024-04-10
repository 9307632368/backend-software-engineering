"""Book catalog example with typed response models and OpenAPI metadata."""
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

class BookCreate(BaseModel):
    title: str = Field(min_length=2, max_length=120, examples=["Designing Data-Intensive Applications"])
    author: str = Field(min_length=2, max_length=80, examples=["Martin Kleppmann"])

class Book(BookCreate):
    id: int

class BookPage(BaseModel):
    items: list[Book]
    count: int

def create_app() -> FastAPI:
    api = FastAPI(title="Book Catalog API", version="1.0.0",
                  description="Small example showing OpenAPI docs, response models, and integration tests.")
    books: dict[int, Book] = {}
    next_id = 1

    @api.post("/books", response_model=Book, status_code=201,
              responses={422: {"description": "Invalid book input"}}, tags=["books"])
    def add_book(data: BookCreate):
        nonlocal next_id
        book = Book(id=next_id, **data.model_dump())
        books[next_id] = book
        next_id += 1
        return book

    @api.get("/books", response_model=BookPage, tags=["books"])
    def list_books(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=50)):
        values = list(books.values())
        return BookPage(items=values[skip:skip + limit], count=len(values))

    @api.get("/books/{book_id}", response_model=Book, responses={404: {"description": "Not found"}}, tags=["books"])
    def get_book(book_id: int):
        if book_id not in books:
            raise HTTPException(404, "Book not found")
        return books[book_id]

    @api.delete("/books/{book_id}", status_code=204, tags=["books"])
    def delete_book(book_id: int):
        if books.pop(book_id, None) is None:
            raise HTTPException(404, "Book not found")

    return api

app = create_app()
