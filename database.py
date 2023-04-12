import pymongo
import pymongo.errors
import os
import csv

from pymongo.collection import Collection

from dotenv import load_dotenv

from datetime import datetime, timedelta
from bson.objectid import ObjectId #for testing

load_dotenv()
MONGO_STR = os.getenv("MONGO_STR")

CYCLE_TIMEOUT = timedelta(minutes=10) # 1 hour

client, db = None, None
coffee_table: Collection = None
capsule_table: Collection = None
user_table: Collection = None
cycle_table:Collection = None
command_table: Collection = None


def init():
    global client, db, coffee_table, capsule_table, user_table, command_table, cycle_table
    client = connect()

    db = client["1234-bot"]

    coffee_table = db["coffee"]
    capsule_table = db["capsule"]
    user_table = db["user"]
    cycle_table = db["cycle"]
    command_table = db["command"]


def connect() -> pymongo.MongoClient:
    client = pymongo.MongoClient(MONGO_STR)
    return client


# -----USER MANAGEMENT-----#
def new_user(user_id, name, surname="", username=""):
    return


# ----- COMMAND MANAGEMENT -----#
# store a element of a user command in the database
def new_command(user_id, command_id, coffee, capsule, tasse):
    return


def return_command(command_id):
    return


# ----- STATE MANAGEMENT -----#

# return the command_id of the cycle
def start_cycle(date):
    if cycle_table.find_one({"end_date": None}) is not None:
        return "Cycle already started"
    cycle_table.insert_one({"start_date": date, "end_date": None})
    return cycle_table.find_one({"end_date": None})["_id"]


def stop_cycle(command_id, date):
    print(cycle_table.find_one({"_id": command_id})["start_date"])
    cycle_table.update_one({"_id": command_id}, {"$set": {"end_date": date}})
    return 


# return the actual command_id and date creation or none if no cycle started
def return_state():
    cycle = cycle_table.find_one({"end_date": None})
    return cycle if cycle is None else (cycle["_id"], cycle["start_date"])

def check_timeout():
    state = return_state()
    if state == None:
        return "No timeout"
    if (datetime.now() - state[1]) > CYCLE_TIMEOUT:
        stop_cycle(state[0], datetime.now())
        return str(state[0]) + " timeout"
    else :
        return "No timeout"


# ----- COFFEE MANAGEMENT -----#

# Enumerate the choice of coffee - return list of string of coffee + default capsule
def read_coffees() -> list[dict[id, str, id, bool]]:
    return list(coffee_table.find())

def add_coffees(coffee, capsule=None, option=False):
    if capsule is not None:
        capsule_id = capsule_table.find_one({"name": capsule})["_id"]
        if capsule_id is None:
            return "Capsule not found"
    else:
        capsule_id = None

def coffee_from_short_name(short_name):
    """Return the name of the coffee from the id"""
    return coffee_table.find_one({"short_name": short_name})["name"]

    coffee_table.insert_one({"name": coffee, "capsule": capsule_id, "option": option})
    return "Success"


# ----- CAPSULE MANEGEMENT -----#

# enumerate the choice of capsule - return list of string of capsule
def read_capsules() -> list[dict[id, str, str]]:
    return list(capsule_table.find())


def add_capsules(capsule, short_name):
    if capsule_table.find_one({"short_name": short_name}) is not None:
        return "Capsule already exist"
    capsule_table.insert_one({"name": capsule, "short_name": short_name})
    return "Success"

# ----- INIT FUNCTION -----#
#Use only to create again database - WARNING cancel all data !!!
def init_database():
    capsule_table.delete_many({})
    coffee_table.delete_many({})
    print("Database deleted")

    with open('resources/database/capsule.csv', 'r') as f:
        reader = csv.DictReader(f)
        capsules_data = [row for row in reader]
    with open('resources/database/coffee.csv', 'r') as f:
        reader = csv.DictReader(f)
        coffees_data = [row for row in reader]

    short_name_capsule = set()
    short_name_coffee = set()
    
    for capsule_data in capsules_data:
        if capsule_data['short_name'] in short_name_capsule:
            print("Capsule short name not unique")
            return
        else:
            short_name_capsule.add(capsule_data['short_name'])

    capsule_table.insert_many(capsules_data)
    print("Capsule added")
    
    for coffee_data in coffees_data:
        if coffee_data['short_name'] in short_name_coffee:
            print("Coffee short name not unique")
            return
        else:
            short_name_coffee.add(coffee_data['short_name'])
            if coffee_data['capsule'] != "":
                if capsule_table.find_one({"name": coffee_data['capsule']}) is None:
                    print("Capsule "+ coffee_data['capsule'] +" not found")
                    return
                coffee_data['capsule'] = capsule_table.find_one({"name": coffee_data['capsule']})['_id']
            else:
                coffee_data['capsule'] = None

    coffee_table.insert_many(coffees_data)
    print("Coffee added")



def test_connection(client) -> str:
    try:
        client.server_info()
        text = "Connected to MongoDB!"
    except pymongo.errors.ServerSelectionTimeoutError:
        text = "Could not connect to MongoDB."
    return text


if __name__ == "__main__":
    # print(test_connection(connect()))
    init()
    print("-----")