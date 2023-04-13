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
consts.CYCLE_OWN_ORDERS = "own_orders_cycle"

consts.ORDER_START = "start_order"
consts.ORDER_VALIDATION = "validate_order"
consts.ORDER_CONFIRM = "confirm_order"
consts.ORDER_DROP = "drop_order"
consts.ORDER_CANCEL = "cancel_order"

consts.GLOU_COMMAND = "glou"


def parse_data_text(data_text: str) -> list:
    """Parse the data text."""
    return data_text.split(consts.SEPARATOR)


def display_order(data: list) -> str:
    """Display the order."""
    text = f"- {database.coffee_from_short_name(data[len(data) - 1])}\n"
    for i in range(len(data) - 2, -1, -1):
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
    coffee_options = sorted(database.read_coffees(), key=lambda k: not k['option'])
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
                                             callback_data=get_callback(consts.COFFEE_COMMAND,
                                                                        str(layout[i][j]["short_name"]), data)))
        keyboard.append(line)
    return InlineKeyboardMarkup(keyboard)


def create_button(text: str, callback_data: str) -> InlineKeyboardButton:
    """Create a button."""
    return InlineKeyboardButton(text, callback_data=callback_data)


def get_start_order_keyboard(user_id) -> InlineKeyboardMarkup:
    """Create the launch order button."""
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Je veux un café ☕️", callback_data=get_callback(consts.GLOU_COMMAND))],
        [InlineKeyboardButton("Voir mes commandes en cours 🕓",
                              callback_data=get_callback(consts.COFFEE_COMMAND, consts.CYCLE_OWN_ORDERS))],
    ])
    return reply_markup


def append_buttons(keyboard: InlineKeyboardMarkup, buttons: list) -> InlineKeyboardMarkup:
    """Add buttons to the keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[*keyboard.inline_keyboard, buttons])


def init_order() -> InlineKeyboardMarkup:
    """Init the order."""
    return append_buttons(append_buttons(get_coffee_options_keyboard(), [
        create_button("❌ En fait je ne veux pas de café ❌", get_callback(consts.COFFEE_COMMAND, consts.ORDER_DROP))]),
                          [create_button("Voir les commandes", get_callback(consts.COFFEE_COMMAND, consts.CYCLE_LIST))])


def get_list() -> str:
    """Get the list of orders."""
    orders = database.return_all_command()
    if len(orders) == 0:
        return "Aucune commande n'a été passée pour le moment"
    else:
        text = "Liste des commandes\n\n"
        for order in orders:
            text += f"{order['user_name']}"
            text += f" avec une capsule {order['capsule']}\n" if order['capsule'] is not None else "\n"
            text += display_order(order['coffee']) + "\n"
        return text


def handle_callback_query_coffee(data: list, user_id: int = None) -> (str, InlineKeyboardMarkup):
    """Choose a coffee"""
    match data[0]:
        case consts.CYCLE_START:
            database.start_cycle()
            return "Les cafés sont lancés ! Quel café veux-tu ?", init_order()
        case consts.CYCLE_DROP:
            return "Pas de souci, n'hésite pas à faire signe quand tu voudras des cafés !", get_start_order_keyboard(user_id)
        case consts.CYCLE_STOP:
            text = "Les commandes sont finies !\n\n"
            text += get_list()
            database.stop_cycle()
            return text, get_start_order_keyboard(user_id)
        case consts.CYCLE_LIST:
            return get_list(), append_buttons(InlineKeyboardMarkup([]),
                                              [create_button("Back", get_callback(consts.GLOU_COMMAND)),
                                               create_button("Stop",
                                                             get_callback(consts.COFFEE_COMMAND, consts.CYCLE_STOP))])
        case consts.CYCLE_OWN_ORDERS:
            orders = database.return_all_command()
            keyboard = [[InlineKeyboardButton("Back", callback_data=get_callback(consts.COFFEE_COMMAND, consts.ORDER_DROP))]] # TODO change order_drop
            if len(orders) == 0:
                return "Tu n'as pas de commandes en cours", get_start_order_keyboard(user_id)
            else:
                text = "Liste de tes commandes en cours\n\n"
                for order in orders:
                    text += "Command"
                    text += f" avec une capsule {order['capsule']}\n" if order['capsule'] is not None else "\n"
                    text += display_order(order['coffee']) + "\n"
                    keyboard.append([InlineKeyboardButton(f"Annuler la tasse {order['capsule']}", callback_data=get_callback(consts.COFFEE_COMMAND, consts.ORDER_CANCEL, order['capsule']))])
                return text, InlineKeyboardMarkup(keyboard)
        case consts.ORDER_VALIDATION:
            coffees = data[1:]
            text = "Récapitulatif de ta commande :\n" + display_order(coffees)
            keyboard = [
                [InlineKeyboardButton("Recommencer ❌", callback_data=get_callback(consts.GLOU_COMMAND)),
                 InlineKeyboardButton("Ajouter ➕", callback_data=get_callback(consts.COFFEE_COMMAND, None, coffees)),
                 InlineKeyboardButton("Confirmer ✅",
                                      callback_data=get_callback(consts.COFFEE_COMMAND, consts.ORDER_CONFIRM,
                                                                 coffees))],
            ]
            if len(coffees) > 1:
                for i in range(len(coffees) - 2, -1, -1):
                    keyboard.append([InlineKeyboardButton("➖ " + database.coffee_from_short_name(coffees[i]),
                                                          callback_data=get_callback(consts.COFFEE_COMMAND,
                                                                                     consts.ORDER_VALIDATION,
                                                                                     coffees[:i] + coffees[i + 1:]))])

            return text, InlineKeyboardMarkup(keyboard)
        case consts.ORDER_CONFIRM:
            capsule = None
            for i in range(len(data) - 1, 0, -1):
                capsule = database.capsule_short_name_from_coffee_short_name(data[i])
                if capsule is not None:
                    break
            database.new_command(user_id, capsule, data[1:])
            return "Ta commande a bien été prise en compte !", get_start_order_keyboard(user_id)
        case consts.ORDER_DROP:
            return "N'hésite pas à cliquer ci-dessous si tu veux du café !", get_start_order_keyboard(user_id)
        case consts.ORDER_CANCEL:
            database.delete_command(user_id, data[1])
            return "Ta commande a bien été annulée !", get_start_order_keyboard(user_id)
        case _ if database.ongoing_cycle():
            # sort data to have options at the end
            text = "Ta commande pour le moment\n"
            text += display_order(data)
            text += "\nVeux-tu ajouter quelque chose ?"
            return text, append_buttons(get_coffee_options_keyboard(options=True, data=data),
                                        [create_button("⬅️ Annuler ❌",
                                                       get_callback(consts.COFFEE_COMMAND, consts.ORDER_DROP)),
                                         create_button("✅ Valider ➡️",
                                                       get_callback(consts.COFFEE_COMMAND, consts.ORDER_VALIDATION,
                                                                    data))])
        case _:  # no ongoing cycle
            return get_coffee_options()


def get_coffee_waiting_keyboard() -> InlineKeyboardMarkup:
    """Get the coffee waiting keyboard."""
    keyboard = [[InlineKeyboardButton("Oh no... Je m'en occupe ☕️ ➡️",
                                      callback_data=get_callback(consts.COFFEE_COMMAND, consts.CYCLE_START))],
                [InlineKeyboardButton("Ah... Je vais prendre un thé alors 🫖 ❌",
                                      callback_data=get_callback(consts.COFFEE_COMMAND, consts.CYCLE_DROP))]]
    return InlineKeyboardMarkup(keyboard)


if __name__ == '__main__':
    print(get_callback("command", "adddata", ["data1", "data2"]))
    print(get_callback("command", "adddata", None))
