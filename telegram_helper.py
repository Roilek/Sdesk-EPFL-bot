from telegram import InlineKeyboardButton, InlineKeyboardMarkup

import database

COFFEE_OPTIONS_KEYBOARD_COLUMNS = 2


def get_coffee_options_keyboard() -> InlineKeyboardMarkup:
    """Get the coffee options keyboard."""
    coffee_options = database.get_coffee_options()
    keyboard = []
    # Split the list into sublists of size COFFEE_OPTIONS_KEYBOARD_COLUMNS
    for i in range(0, len(coffee_options), COFFEE_OPTIONS_KEYBOARD_COLUMNS):
        keyboard.append(coffee_options[i:i + COFFEE_OPTIONS_KEYBOARD_COLUMNS])
    # Convert the list of tuples into a list of InlineKeyboardButton
    for i in range(len(keyboard)):
        for j in range(len(keyboard[i])):
            keyboard[i][j] = InlineKeyboardButton(keyboard[i][j][1], callback_data="coffee_"+str(keyboard[i][j][0]))
    return InlineKeyboardMarkup(keyboard)


def choose_coffee(text) -> str:
    return f"Tu as choisi le café: {text}"
