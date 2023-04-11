import pymongo
import pymongo.errors
import os

from dotenv import load_dotenv

load_dotenv()
MONGO_STR = os.getenv("MONGO_STR")


def connect() -> pymongo.MongoClient:
    client = pymongo.MongoClient(MONGO_STR)
    return client


def test_connection(client) -> str:
    try:
        client.server_info()
        text = "Connected to MongoDB!"
    except pymongo.errors.ServerSelectionTimeoutError:
        text = "Could not connect to MongoDB."
    return text


if __name__ == "__main__":
    print(test_connection(connect()))
