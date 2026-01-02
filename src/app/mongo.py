import os
from typing import Annotated
from fastapi.params import Depends
from pymongo import AsyncMongoClient
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase


class MongoConfig:
    def __init__(self, host: str):
        self.host = host


async def mongo_config() -> MongoConfig:
    return MongoConfig(os.environ["Mongo_Host"])


async def mongo_client(
    config: Annotated[
        MongoConfig,
        Depends(mongo_config)]
) -> AsyncMongoClient:
    return AsyncMongoClient(config.host)


async def mongo_database(
    mongoClient: Annotated[
        AsyncMongoClient,
        Depends(mongo_client)]
) -> AsyncDatabase:
    return mongoClient.get_database("bookStore")


async def books_colllection(
    mongo_database: Annotated[AsyncDatabase, Depends(mongo_database)]
) -> AsyncCollection:
    return mongo_database.get_collection("books")
