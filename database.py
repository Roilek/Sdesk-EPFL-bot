import pymongo
import pymongo.errors
import os

from dotenv import load_dotenv

load_dotenv()
MONGO_STR = os.getenv("MONGO_STR")

client, db, coffee_table, capsule_table, user_table, command_table = None, None, None, None, None, None

def init():
    global client, db, coffee_table, capsule_table, user_table, command_table
    client = connect()

    db = client["1234-bot"]

    coffee_table = db["coffee"]
    capsule_table = db["capsule"]
    user_table = db["user"]
    command_table = db["command"]


def connect() -> pymongo.MongoClient:
    client = pymongo.MongoClient(MONGO_STR)
    return client


#-----USER MANAGEMENT-----#
def new_user(user_id, name, surname="", username=""):
    return

#----- COMMAND MANAGEMENT -----#
#store a element of a user command in the database
def new_command(user_id, command_id, coffee, capsule, tasse):
    return

#----- STATE MANEGEMENT -----#

#return the command_id of the cycle
def new_cycle(date):
    return

def stop_cycle(command_id, date):
    return

#return the actual command_id and date creation or none if no cycle started
def return_state():
    return

#----- COFFEE MANAGEMENT -----#

#Enumerate the choice of coffee - return list of string of coffee + default capsule
def read_coffees():
    return list(coffee_table.find())

def add_coffees(coffee, capsule):
    capsule_id = capsule_table.find_one({"name": capsule})["_id"]
    if capsule_id is None:
        return "Capsule not found"
    coffee_table.insert_one({"name": coffee, "capsule": capsule_id})
    return "Success"

#----- CAPSULE MANEGEMENT -----#

#enumerate the choice of capsule - return list of string of capsule
def read_capsules():
    return list(capsule_table.find())

def add_capsules(capsule):
    capsule_table.insert_one({"name": capsule})
    return "Success"

def test_connection(client) -> str:
    try:
        client.server_info()
        text = "Connected to MongoDB!"
    except pymongo.errors.ServerSelectionTimeoutError:
        text = "Could not connect to MongoDB."
    return text


if __name__ == "__main__":
    print(test_connection(connect()))
    init()
    print(read_capsules())
