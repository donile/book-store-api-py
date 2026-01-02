from http import HTTPStatus
import os
from typing import Generator, Iterable, List
from bson import ObjectId
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
import pytest
from app.books.book import Book
from app.main import api
from fastapi.testclient import TestClient
from testcontainers.mongodb import MongoDbContainer
from app.mongo import MongoConfig


@pytest.fixture(autouse=True, scope="session")
def mongo_container() -> Generator[MongoDbContainer, None, None]:
    with MongoDbContainer("mongo:8.2.2-noble") as mongo:
        yield mongo


@pytest.fixture(autouse=True, scope="session")
def mongo_config(mongo_container: MongoDbContainer) -> MongoConfig:
    mongo_host = mongo_container.get_connection_url()
    os.environ["Mongo_Host"] = mongo_host
    return MongoConfig(mongo_host)


@pytest.fixture(autouse=True, scope="session")
def mongo_client(mongo_config: MongoConfig) -> MongoClient:
    return MongoClient(mongo_config.host)


@pytest.fixture(autouse=True, scope="session")
def book_store_db(mongo_client: MongoClient) -> Database:
    return mongo_client.get_database("bookStore")


@pytest.fixture(autouse=True, scope="session")
def books() -> List[Book]:
    return [
        Book(title="Dead Simple Python", author="Jason McDonald"),
        Book(title="Hitchiker's Guide to the Galaxy", author="Douglas Adams")
    ]


@pytest.fixture(autouse=True, scope="function")
def book_collection(
        book_store_db: Database,
        books: Iterable[Book]) -> Collection:
    collection = book_store_db.get_collection("books")
    collection.drop()
    collection.insert_many([book.model_dump() for book in books])
    return collection


@pytest.fixture()
def http_client() -> TestClient:
    return TestClient(api)


def test_get_books(http_client: TestClient):
    response = http_client.get("/books")
    assert response.status_code == 200
    assert response.json() == [
        {
            "title": "Dead Simple Python",
            "author": "Jason McDonald"
        },
        {
            "title": "Hitchiker's Guide to the Galaxy",
            "author": "Douglas Adams"
        }
    ]


def test_post_book(http_client: TestClient, book_collection: Collection):
    book = {
        "title": "new title",
        "author": "new author"
    }
    response = http_client.post("/books", json=book)
    book_id = response.headers["Location"].split("/")[-1]
    book["_id"] = ObjectId(book_id)
    assert response.status_code == 201
    assert book_collection.find_one({"_id": ObjectId(book_id)}) == book


def test_put_book(http_client: TestClient, book_collection: Collection):
    book_doc = book_collection.find_one({})
    book_id = book_doc["_id"]
    book = {
        "title": "updated title",
        "author": "updated author"
    }
    response = http_client.put(f"/books/{book_id}", json=book)
    book["_id"] = book_id
    assert response.status_code == HTTPStatus.NO_CONTENT
    assert book_collection.find_one({"_id": book_id}) == book


def test_delete_book(http_client: TestClient, book_collection: Collection):
    book_doc = book_collection.find_one({})
    book_id = book_doc["_id"]
    response = http_client.delete(f"/books/{book_id}")
    assert response.status_code == HTTPStatus.NO_CONTENT
    assert book_collection.find_one({"_id": book_id}) is None
