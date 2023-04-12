from telegram import InlineKeyboardButton, InlineKeyboardMarkup

import database

import types

consts = types.SimpleNamespace()

consts.SEPARATOR = '#'

consts.COFFEE_OPTIONS_KEYBOARD_COLUMNS = 2

consts.COFFEE_COMMAND = "coffee"

consts.CYCLE_START = "start_cycle"
consts.CYCLE_STOP = "stop_cycle"
consts.CYCLE_DROP = "drop_cycle"
consts.CYCLE_LIST = "list_cycle"

consts.ORDER_START = "start_order"
consts.ORDER_VALIDATION = "validate_order"
consts.ORDER_CONFIRM = "confirm_order"
consts.ORDER_DROP = "drop_order"

consts.GLOU_COMMAND = "glou"


def parse_data_text(data_text: str) -> list:
    """Parse the data text."""
    return data_text.split(consts.SEPARATOR)


def display_order(data: list) -> str:
    """Display the order."""
    text = f"- {database.coffee_from_short_name(data[len(data)-1])}\n"
    for i in range(len(data)-2, -1, -1):
        text += f"\t+ {database.coffee_from_short_name(data[i])}\n"
    return text


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
            return consts.SEPARATOR.join([command, add_data, *data])


def get_coffee_options() -> (str, InlineKeyboardMarkup):
    if not database.ongoing_cycle():
        return "Aucune commande n'est en cours", get_coffee_waiting_keyboard()
    else:
        return "Quelle sera ta source d'énergie aujourd'hui ?", init_order()


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


def get_start_order_keyboard() -> InlineKeyboardMarkup:
    """Create the launch order button."""
    return InlineKeyboardMarkup([[create_button("Je veux des cafés ☕️", get_callback(consts.GLOU_COMMAND))]])

def append_buttons(keyboard: InlineKeyboardMarkup, buttons: list) -> InlineKeyboardMarkup:
    """Add buttons to the keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[*keyboard.inline_keyboard, buttons])


def init_order() -> InlineKeyboardMarkup:
    """Init the order."""
    return append_buttons(append_buttons(get_coffee_options_keyboard(), [create_button("❌ Finalement je prends un thé ❌", get_callback(consts.COFFEE_COMMAND, consts.ORDER_DROP))]), [create_button("Voir les commandes", get_callback(consts.COFFEE_COMMAND, consts.CYCLE_LIST))])

def handle_callback_query_coffee(data: list, user_id: int = None) -> (str, InlineKeyboardMarkup):
    """Choose a coffee"""
    match data[0]:
        case consts.CYCLE_START:
            database.start_cycle()
            return "Les cafés sont lancés ! Quel café veux-tu ?", init_order()
        case consts.CYCLE_DROP:
            return "Pas de souci, n'hésite pas à faire signe quand tu voudras des cafés !", get_start_order_keyboard()
        case consts.CYCLE_STOP:
            database.stop_cycle()
            return "Les commandes sont arrêtées !", get_start_order_keyboard()
        case consts.CYCLE_LIST:
            text = "Liste des commandes :\n"
            orders = database.return_all_command()
            if len(orders) == 0:
                return "Aucune commande n'a été passée", get_start_order_keyboard()
            for order in orders:
                print(order)
                text += f"- {order['user_id']} with {order['capsule']} : {display_order(order['short_name'])}\n"
            return text, append_buttons(InlineKeyboardMarkup([]), [create_button("Arrêter les commandes", get_callback(consts.CYCLE_STOP)), create_button("Actualiser les commandes", get_callback(consts.CYCLE_LIST))])
        case consts.ORDER_VALIDATION:
            return "Récapitulatif de ta commande :\n" + display_order(data[1:]), append_buttons(InlineKeyboardMarkup([]), [create_button("Confirmer ✅", get_callback(consts.COFFEE_COMMAND, consts.ORDER_CONFIRM, data[1:])), create_button("Recommencer ❌", get_callback(consts.GLOU_COMMAND))])
        case consts.ORDER_CONFIRM:
            print(f"Adding {data[1:]} for {user_id}")
            database.new_command(user_id, database.capsule_short_name_from_coffee_short_name(data[1]), data[1:])
            return "Ta commande a bien été prise en compte !", get_start_order_keyboard()
        case consts.ORDER_DROP:
            return "Ta commande a été annulée ! N'hésite pas à faire signe quand tu voudras des cafés !", get_start_order_keyboard()
        case _ if database.ongoing_cycle():
            text = "Ta commande pour le moment\n"
            text += display_order(data)
            text += "\nVeux-tu ajouter quelque chose ?"
            return text, append_buttons(get_coffee_options_keyboard(options=True, data=data),
                                        [create_button("⬅️ Annuler ❌", get_callback(consts.COFFEE_COMMAND, consts.ORDER_DROP)),
                                         create_button("✅ Valider ➡️", get_callback(consts.COFFEE_COMMAND, consts.ORDER_VALIDATION, data))])
        case _: # no ongoing cycle
            return get_coffee_options()


def get_coffee_waiting_keyboard() -> InlineKeyboardMarkup:
    """Get the coffee waiting keyboard."""
    keyboard = [[InlineKeyboardButton("Oh no... Je m'en occupe ☕️ ➡️", callback_data=get_callback(consts.COFFEE_COMMAND, consts.CYCLE_START))],
                [InlineKeyboardButton("Ah... Je vais prendre un thé alors 🫖 ❌", callback_data=get_callback(consts.COFFEE_COMMAND, consts.CYCLE_DROP))]]
    return InlineKeyboardMarkup(keyboard)


if __name__ == '__main__':
    print(get_callback("command", "adddata", ["data1", "data2"]))
    print(get_callback("command", "adddata", None))
