from fastapi import FastAPI

from app import books


api = FastAPI()
api.include_router(books.router)
