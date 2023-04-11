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


# To remove, for dev purposes only
def get_coffee_options() -> list[(int, str, int)]:
    """Get the coffee options from the database."""
    # return fake data
    return [
        (1, "Café", 1),
        (2, "Café au lait", 2),
        (3, "Café au lait sucré", 3),
        (4, "Café au lait sucré et chocolaté", 4),
        (5, "Café au lait sucré et chocolaté avec un biscuit", 5),
        (6, "Café au lait sucré et chocolaté avec un biscuit et une crème chantilly", 6),
        (7, "Café au lait sucré et chocolaté avec un biscuit, une crème chantilly et un petit nuage", 7)]
