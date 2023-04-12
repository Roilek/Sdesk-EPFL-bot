import pymongo
import pymongo.errors
import os
import csv

from pymongo.collection import Collection

from dotenv import load_dotenv

from datetime import datetime, timedelta

load_dotenv()
MONGO_STR = os.getenv("MONGO_STR")

CYCLE_TIMEOUT = timedelta(minutes=10)  # 1 hour

client, db = None, None
coffee_table: Collection = None
capsule_table: Collection = None
user_table: Collection = None
cycle_table: Collection = None
command_table: Collection = None
favorite_table: Collection = None


def init():
    global client, db, coffee_table, capsule_table, user_table, command_table, cycle_table, favorite_table
    client = connect()

    db = client["1234-bot"]

    coffee_table = db["coffee"]
    capsule_table = db["capsule"]
    user_table = db["user"]
    cycle_table = db["cycle"]
    command_table = db["command"]
    favorite_table = db["favorite"]


def connect() -> pymongo.MongoClient:
    client = pymongo.MongoClient(MONGO_STR)
    return client


# -----USER MANAGEMENT-----#
def new_user(user_id, name, surname="", username=""):
    user_table.insert_one({"user_id": user_id, "name": name, "surname": surname, "username": username})
    return


def delete_user(user_id):
    user_table.delete_one({"user_id": user_id})
    return


# ----- COMMAND MANAGEMENT -----#
# store a element of a user command in the database
def new_command(user_id, capsule, list_command):
    actual_command = return_user_commande(user_id)
    if actual_command is not None:
        tasse = len(command_table.distinct("tasse", {"user_id": user_id}))
    else:
        tasse = 0
    for command in list_command:
        coffee = command
        new_object_command(user_id, coffee, capsule, tasse)
    return


def new_object_command(user_id, coffee, capsule, tasse):
    coffee = coffeeid_from_short_name(coffee)
    if capsule is not None:
        capsule = capsuleid_from_short_name(capsule)
    if ongoing_cycle():
        command_id = return_commandid()
    else:
        return "No cycle"
    command_table.insert_one(
        {"user_id": user_id, "command_id": command_id, "coffee": coffee, "capsule": capsule, "tasse": tasse})
    return "Success"


def delete_command(user_id, tasse):
    if ongoing_cycle():
        command_id = return_commandid()
    else:
        return
    command_table.delete_many({"user_id": user_id, "command_id": command_id, "tasse": tasse})
    return


def return_all_command() -> list[dict[str, str, list[str]]]:
    # user_id, capsule, coffee
    if ongoing_cycle():
        command_id = return_commandid()
    else:
        return []
        # Return a list of commands with coffee field grouped by user_id and command_id and tasse
    list = []

    user = command_table.distinct('user_id', {"command_id": command_id})
    for user_id in user:
        tasses = command_table.distinct('tasse', {"command_id": command_id, "user_id": user_id})
        for tasse in tasses:
            commands = command_table.find({"command_id": command_id, "user_id": user_id, "tasse": tasse})
            capsule = None if commands[0]['capsule'] is None else (capsule_table.find_one({"_id": commands[0]['capsule']})['name']) 
            list_temp = []
            for command in commands:
                list_temp.append(coffee_table.find_one({"_id": command['coffee']})['short_name'])
            user_name = user_table.find_one({"user_id":user_id})['name']
            list.append({"user_name": user_name, "capsule": capsule, "coffee": list_temp})
    return list


def return_user_commande(user_id):
    if ongoing_cycle():
        command_id = return_commandid()
    else:
        return
    return command_table.find({"command_id": command_id, "user_id": user_id})


def return_all_user_command(user_id):
    return command_table.find({"user_id": user_id})


# ----- STATE MANAGEMENT -----#

# return the command_id of the cycle
def start_cycle():
    if cycle_table.find_one({"end_date": None}) is not None:
        return "Cycle already started"
    cycle_table.insert_one({"start_date": datetime.now(), "end_date": None})
    return "Cycle started"


def stop_cycle():
    command_id = return_commandid()
    if command_id is None:
        return "No cycle"
    cycle_table.update_one({"_id": command_id}, {"$set": {"end_date": datetime.now()}})
    return "Cycle stopped"


def ongoing_cycle():
    return cycle_table.find_one({"end_date": None}) is not None


def return_commandid():
    cycle = cycle_table.find_one({"end_date": None})
    return cycle["_id"] if cycle is not None else None


def check_timeout():
    command_id = return_commandid()
    if command_id == None:
        return "No cycle"
    start_time = cycle_table.find_one({"_id": command_id})["start_date"]
    if (datetime.now() - start_time) > CYCLE_TIMEOUT:
        stop_cycle()
        return str(command_id) + " timeout"
    else:
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

    coffee_table.insert_one({"name": coffee, "capsule": capsule_id, "option": option})
    return "Success"


def coffeeid_from_short_name(short_name):
    """Return the id of the coffee from the short name"""
    return coffee_table.find_one({"short_name": short_name})["_id"]


def coffee_from_short_name(short_name):
    """Return the name of the coffee from the id"""
    return coffee_table.find_one({"short_name": short_name})["name"]


def capsule_short_name_from_coffee_short_name(short_name):
    """Return the capsule of the coffee from the short name"""
    capsule = coffee_table.find_one({"short_name": short_name})["capsule"]
    return capsule_table.find_one({"_id": capsule})["short_name"] if capsule is not None else None


# ----- CAPSULE MANAGEMENT -----#

# enumerate the choice of capsule - return list of string of capsule
def read_capsules() -> list[dict[id, str, str]]:
    return list(capsule_table.find())


def add_capsules(capsule, short_name):
    if capsule_table.find_one({"short_name": short_name}) is not None:
        return "Capsule already exist"
    capsule_table.insert_one({"name": capsule, "short_name": short_name})
    return "Success"


def capsuleid_from_short_name(short_name):
    """Return the id of the capsule from the short name"""
    return capsule_table.find_one({"short_name": short_name})["_id"]


def capsule_from_short_name(short_name):
    """Return the name of the capsule from the id"""
    return capsule_table.find_one({"short_name": short_name})["name"]


# ----- FAVORITE MANAGEMENT -----#
def add_favorite(user_id, tasse):
    command_id = return_commandid()


# ----- INIT FUNCTION -----#
# Use only to create again database - WARNING cancel all data !!!
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
        # check if short name is unique
        if capsule_data['short_name'] in short_name_capsule:
            print("Capsule short name not unique")
            return
        else:
            short_name_capsule.add(capsule_data['short_name'])

    capsule_table.insert_many(capsules_data)
    print("Capsule added")

    for coffee_data in coffees_data:
        # transform string to boolean
        coffee_data['option'] = coffee_data['option'] == 'True'
        # check if short name is unique
        if coffee_data['short_name'] in short_name_coffee:
            print("Coffee short name not unique")
            return
        else:
            short_name_coffee.add(coffee_data['short_name'])
            # check if capsule exist and transform to capsule objectId
            if coffee_data['capsule'] != "":
                if capsule_table.find_one({"name": coffee_data['capsule']}) is None:
                    print("Capsule " + coffee_data['capsule'] + " not found")
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
    print(return_all_command())
