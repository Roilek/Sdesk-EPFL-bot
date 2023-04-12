from telegram import InlineKeyboardButton, InlineKeyboardMarkup

import database

import types

consts = types.SimpleNamespace()

consts.SEPARATOR = '#'

consts.COFFEE_OPTIONS_KEYBOARD_COLUMNS = 2

consts.COFFEE_COMMAND = "coffee"

consts.COFFEE_START = "start_session"
consts.COFFEE_STOP = "stop_session"
consts.COFFEE_DROP = "drop_session"
consts.COFFEE_LIST = "list_session"

consts.ORDER_START = "start_order"
consts.ORDER_VALIDATE = "validate_order"
consts.ORDER_DROP = "drop_order"

consts.GLOU_COMMAND = "glou"


def parse_data_text(data_text: str) -> list:
    """Parse the data text."""
    return data_text.split(consts.SEPARATOR)


def get_callback(command: str, add_data: str = None, data: list = None) -> str:
    """Get the callback data."""
    if add_data is None:
        if data is None:
            return command
        else:
            return consts.SEPARATOR.join([command, *data])
    else:
        if data is None:
            return consts.SEPARATOR.join([command, add_data])
        else:
            return consts.SEPARATOR.join([command, *data, add_data])


def get_coffee_options_keyboard(options: bool = False, data: list = None) -> InlineKeyboardMarkup:
    """Get the coffee options keyboard."""
    if data is None:
        data = []
    coffee_options = database.read_coffees()
    # Filter the coffee options if needed
    if not options:
        coffee_options = [option for option in coffee_options if not option["option"]]
    layout = []
    # Split the list into sublists of size COFFEE_OPTIONS_KEYBOARD_COLUMNS
    for i in range(0, len(coffee_options), consts.COFFEE_OPTIONS_KEYBOARD_COLUMNS):
        layout.append(coffee_options[i:i + consts.COFFEE_OPTIONS_KEYBOARD_COLUMNS])
    # Convert the list of tuples into a list of InlineKeyboardButton for each line and each column
    keyboard = []
    for i in range(len(layout)):
        line = []
        for j in range(len(layout[i])):
            line.append(InlineKeyboardButton(layout[i][j]["name"],
                                             callback_data=get_callback(consts.COFFEE_COMMAND, str(layout[i][j]["short_name"]), data)))
        keyboard.append(line)
    return InlineKeyboardMarkup(keyboard)


def create_button(text: str, callback_data: str) -> InlineKeyboardButton:
    """Create a button."""
    return InlineKeyboardButton(text, callback_data=callback_data)


def append_buttons(keyboard: InlineKeyboardMarkup, buttons: list) -> InlineKeyboardMarkup:
    """Add buttons to the keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[*keyboard.inline_keyboard, buttons])


def init_order() -> InlineKeyboardMarkup:
    """Init the order."""
    return append_buttons(get_coffee_options_keyboard(), [create_button("❌ Finalement je prends un thé ❌", get_callback(consts.COFFEE_COMMAND, consts.ORDER_DROP))])

def handle_callback_query_coffee(data: list) -> (str, InlineKeyboardMarkup):
    """Choose a coffee"""
    new_data = data[0]
    match data[0]:
        case consts.COFFEE_START:
            from datetime import datetime
            database.start_cycle(datetime.now())
            return "Les cafés sont lancés ! Quel café veux-tu ?", init_order()
        case consts.COFFEE_DROP:
            return "Pas de souci, n'hésite pas à faire signe quand tu voudras des cafés !", append_buttons(InlineKeyboardMarkup([]), [create_button("Je veux des cafés ☕️", get_callback(consts.GLOU_COMMAND))])
        case consts.COFFEE_STOP:
            from datetime import datetime
            database.stop_cycle(1234, datetime.now())
            return "Les commandes sont terminées !", append_buttons(InlineKeyboardMarkup([]), [create_button("Voir la liste des commandes", get_callback(consts.COFFEE_LIST))])
        case consts.COFFEE_LIST:
            return database.get_orders(), append_buttons(InlineKeyboardMarkup([]), [create_button("Je veux des cafés ☕️", get_callback(consts.GLOU_COMMAND))])
        case consts.ORDER_START:
            pass
        case consts.ORDER_VALIDATE:
            pass
        case consts.ORDER_DROP:
            return "Ta commande a été annulée ! N'hésite pas à faire signe quand tu voudras des cafés !", append_buttons(InlineKeyboardMarkup([]), [create_button("Je veux des cafés ☕️", get_callback(consts.GLOU_COMMAND))])
        case _:
            text = "Ta commande pour le moment\n"
            text += f"\t{database.coffee_from_short_name(data[0])}\n"
            for i in range(1, len(data)):
                text += f"\t+ {database.coffee_from_short_name(data[i])}\n"
            text += "\nVeux-tu ajouter quelque chose ?"
            return text, append_buttons(get_coffee_options_keyboard(options=True, data=data),
                                        [create_button("⬅️ Annuler ❌", get_callback(consts.COFFEE_COMMAND, consts.ORDER_DROP)),
                                         create_button("✅ Valider ➡️", get_callback(consts.COFFEE_COMMAND, consts.ORDER_VALIDATE, data))])


def get_coffee_waiting_keyboard() -> InlineKeyboardMarkup:
    """Get the coffee waiting keyboard."""
    keyboard = [[InlineKeyboardButton("Oh no... Je m'en occupe ☕️ ➡️", callback_data=get_callback(consts.COFFEE_COMMAND, consts.COFFEE_START))],
                [InlineKeyboardButton("Ah... Je vais prendre un thé alors 🫖 ❌", callback_data=get_callback(consts.COFFEE_COMMAND, consts.COFFEE_DROP))]]
    return InlineKeyboardMarkup(keyboard)


if __name__ == '__main__':
    print(get_callback("command", "adddata", ["data1", "data2"]))
    print(get_callback("command", "adddata", None))
