import os

from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler

import database
import telegram_helper

# Load the environment variables

load_dotenv()

TOKEN = os.getenv("TOKEN")
PORT = int(os.getenv('PORT', 5000))
HEROKU_PATH = os.getenv('HEROKU_PATH')


async def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    # Register new user TODO
    text = "Bienvenue sur le bot du 1234 !\n"
    text += "Ici tu peux commander des super cafés !\n"
    text += "Pour commencer, envoie /glou\n"
    text += "Tu peux également envoyer /help pour plus d'infos !"
    await update.message.reply_text(text)
    return


async def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text('Contactez @eliorpap pour plus d\'infos !')
    return


async def dump(update: Update, context: CallbackContext) -> None:
    """Dump the update object."""
    await update.message.reply_text(f"```{update}```", parse_mode=ParseMode.MARKDOWN_V2)
    return


async def test_connection(update: Update, context: CallbackContext) -> None:
    """Test the connection to MongoDB."""
    await update.message.reply_text(database.test_connection(database.connect()))
    return


async def send_coffee_options(update: Update, context: CallbackContext) -> None:
    """Send the coffe menu."""
    # Get the state of the coffee ordering process
    state = database.return_state()
    # If state is None, send the waiting message
    if state is None:
        text = "Aucune commande n'est en cours"
        await update.message.reply_text(text, reply_markup=telegram_helper.get_coffee_waiting_keyboard())
    # If state is not None, send the coffee options
    else:
        text = "Quelle sera ta source d'énergie aujourd'hui ?"
        await update.message.reply_text(text, reply_markup=telegram_helper.init_order())
    return


async def handle_callback_query(update: Update, context: CallbackContext) -> None:
    """Handle the callback query."""
    query = update.callback_query
    await query.answer()

    data = telegram_helper.parse_data_text(query.data)
    if data[0] == telegram_helper.consts.COFFEE_COMMAND:
        text, keyboard = telegram_helper.handle_callback_query_coffee(data[1:])
        await query.edit_message_text(text, reply_markup=keyboard)
    return


def main() -> None:
    """Start the bot."""
    print("Going live!")

    # Create application
    application = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("dump", dump))
    application.add_handler(CommandHandler("test", test_connection))
    application.add_handler(CommandHandler("glou", send_coffee_options))

    # on query answer - handle the query
    application.add_handler(CallbackQueryHandler(handle_callback_query))


    # Start the Bot
    print("Bot starting...")
    if os.environ.get('ENV') == 'DEV':
        application.run_polling()
    elif os.environ.get('ENV') == 'PROD':
        application.run_webhook(listen="0.0.0.0",
                                port=int(PORT),
                                webhook_url=HEROKU_PATH)
    return


if __name__ == '__main__':
    database.init()
    main()
