#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import logging
# -*- coding: UTF-8 -*-
import os

from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from reports.buttons import button_functions

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN2")
BOT_USERNAME = os.getenv("BOT_USERNAME2")
# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
# Define your buttons and corresponding functions in a dictionary
# Create a list of button texts to be used in ReplyKeyboardMarkup
button_texts = list(button_functions.keys())
buttons = ReplyKeyboardMarkup([button_texts[i:i + 2] for i in range(0, len(button_texts), 2)])


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html((rf"Hi {user.mention_html()}cek!"), reply_markup=buttons)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    button_text = update.message.text
    # Use the button_functions dictionary to get the corresponding function
    button_function = button_functions.get(button_text)

    if button_function:
        # If the function exists, call it
        await button_function(update, context)
    else:
        # Handle the case where the button text doesn't match any function
        await update.message.reply_text(f"No function defined for button: {button_text}")


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
