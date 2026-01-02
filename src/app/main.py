from http import HTTPStatus
from typing import Annotated
from bson import ObjectId
from fastapi import Body, Depends, FastAPI, Path, Response
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase
from app.books.book import Book
from app.mongo import books_colllection, mongo_database

api = FastAPI()


@api.get("/books", status_code=HTTPStatus.OK)
async def get_books(
    mongo_database: Annotated[
        AsyncDatabase,
        Depends(mongo_database),
    ]
) -> list[Book]:
    collection = mongo_database.get_collection("books")
    cursor = collection.find({})
    return [book async for book in cursor]


@api.post("/books", status_code=HTTPStatus.CREATED)
async def post_book(
    book: Annotated[Book, Body()],
    collection: Annotated[AsyncCollection, Depends(books_colllection)],
    response: Response
) -> None:
    doc = book.model_dump()
    await collection.insert_one(doc)
    response.headers["Location"] = f"/books/{doc['_id']}"
    return


@api.put("/books/{book_id}", status_code=HTTPStatus.NO_CONTENT)
async def put_book(
    book_id: Annotated[str, Path()],
    book: Annotated[Book, Body()],
    collection: Annotated[AsyncCollection, Depends(books_colllection)]
) -> None:
    await collection.replace_one({"_id": ObjectId(book_id)}, book.model_dump())
    return


@api.delete("/books/{book_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_book(
    book_id: Annotated[str, Path()],
    collection: Annotated[AsyncCollection, Depends(books_colllection)]
) -> None:
    await collection.delete_one({"_id": ObjectId(book_id)})
    return
