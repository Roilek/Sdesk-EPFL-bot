from telegram import InlineKeyboardButton, InlineKeyboardMarkup

import database

COFFEE_OPTIONS_KEYBOARD_COLUMNS = 2


def get_coffee_options_keyboard() -> InlineKeyboardMarkup:
    """Get the coffee options keyboard."""
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
                                                    callback_data="coffee_"+str(layout[i][j]["_id"])))
        keyboard.append(line)
    return InlineKeyboardMarkup(keyboard)


def choose_coffee(text) -> str:
    return f"Tu as choisi le café: {text}"
