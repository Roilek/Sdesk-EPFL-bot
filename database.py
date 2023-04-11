import pymongo
import pymongo.errors
import os

from dotenv import load_dotenv

load_dotenv()
MONGO_STR = os.getenv("MONGO_STR")


def connect():
    client = pymongo.MongoClient(MONGO_STR)
    return client


def test_connection(client):
    try:
        client.server_info()
        print("Connected to MongoDB!")
    except pymongo.errors.ServerSelectionTimeoutError:
        print("Could not connect to MongoDB.")
    return


if __name__ == "__main__":
    test_connection(connect())
