from telegram import InlineKeyboardButton, InlineKeyboardMarkup

import database

SEPARATOR = '_'

COFFEE_OPTIONS_KEYBOARD_COLUMNS = 2
COFFEE_COMMAND = "coffee"
COFFEE_START = "start"
COFFEE_DROP = "drop"
COFFEE_STOP = "stop"


def parse_data_text(data_text: str) -> list:
    """Parse the data text."""
    return data_text.split(SEPARATOR)


def get_callback(command: str, add_data: str, data: list = None) -> str:
    """Get the callback data."""
    if data is None:
        return SEPARATOR.join([command, add_data])
    else:
        return SEPARATOR.join([command, *data, add_data])


def get_coffee_options_keyboard(options: bool = False, data: list = None) -> InlineKeyboardMarkup:
    """Get the coffee options keyboard."""
    if data is None:
        data = []
    coffee_options = database.read_coffees()
    layout = []
    # Split the list into sublists of size COFFEE_OPTIONS_KEYBOARD_COLUMNS
    for i in range(0, len(coffee_options), COFFEE_OPTIONS_KEYBOARD_COLUMNS):
        layout.append(coffee_options[i:i + COFFEE_OPTIONS_KEYBOARD_COLUMNS])
    # Convert the list of tuples into a list of InlineKeyboardButton for each line and each column
    keyboard = []
    for i in range(len(layout)):
        line = []
        for j in range(len(layout[i])):
            line.append(InlineKeyboardButton(layout[i][j]["name"],
                                             callback_data=get_callback(COFFEE_COMMAND, str(layout[i][j]["_id"]), data)))
        keyboard.append(line)
    return InlineKeyboardMarkup(keyboard)


def choose_coffee(data_text) -> (str, InlineKeyboardMarkup):
    """Choose a coffee"""
    if data_text == COFFEE_START:
        return "Les cafés sont lancés ! Quel café veux-tu ?", get_coffee_options_keyboard()
    elif data_text == COFFEE_DROP:
        return "Dommage, passez quand même un bon shift !", None
    else:
        data = parse_data_text(data_text)
        text = "Ta commande pour le moment\n"
        text += f"\t{database.coffee_from_id(data[0])}\n"
        for i in range(1, len(data)):
            text += f"\t+ {database.coffee_from_id(data[i])}\n"
        text += "\nVeux-tu ajouter quelque chose ?"
        return text, get_coffee_options_keyboard(options=True, data=data)


def get_coffee_waiting_keyboard() -> InlineKeyboardMarkup:
    """Get the coffee waiting keyboard."""
    keyboard = [[InlineKeyboardButton("Oh no... Je m'en occupe !", callback_data=get_callback(COFFEE_COMMAND, COFFEE_START))],
                [InlineKeyboardButton("Ah... Je vais prendre un thé alors...", callback_data=get_callback(COFFEE_COMMAND, COFFEE_DROP))]]
    return InlineKeyboardMarkup(keyboard)


if __name__ == '__main__':
    print(get_callback("command", "adddata", ["data1", "data2"]))
    print(get_callback("command", "adddata", None))
