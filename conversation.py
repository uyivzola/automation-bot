import os
from dotenv import load_dotenv

import logging
from typing import Dict

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackContext,
)

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard = [
    [KeyboardButton("Send Phone Number", request_contact=True)],
    [KeyboardButton("Send Location", request_location=True),
     KeyboardButton("Manually Share Location", request_location=True)],
    ["Done"],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask user for input."""
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)

    await update.message.reply_text(
        "Hello! I am the DFS BOT helper. I need your credentials (these are stored in my user_data.csv file)."
        "First, please send me your phone number using the button below:",
        reply_markup=markup,
    )

    return CHOOSING


async def received_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store user's phone number and ask for the location."""
    contact = update.message.contact
    context.user_data["phone_number"] = contact.phone_number

    await update.message.reply_text(
        f"Great! I got your phone number: {contact.phone_number}\nNow, please share your location with me."
    )

    return CHOOSING


async def received_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store user's location and ask for more information."""
    location = update.message.location
    latitude, longitude = location.latitude, location.longitude

    # Assuming your chat_id is stored in the variable 'chat_id'
    chat_id = update.message.chat_id

    context.user_data["location"] = f"Latitude: {latitude}, Longitude: {longitude}"

    await update.message.reply_text(
        f"Thank you for sharing your location!\n{context.user_data['location']}\n"
        "You can share more information or press 'Done' to finish the conversation.",
        reply_markup=markup,
    )

    return CHOOSING


# Modify the reply keyboard to include a button for sending a photo
reply_keyboard_photo = [
    [KeyboardButton("Send Photo", request_location=True)],
    ["Done"],
]

markup_photo = ReplyKeyboardMarkup(reply_keyboard_photo, one_time_keyboard=True)


# Implement a new function to handle the received selfie photo
async def received_photo(update: Update, context: CallbackContext) -> int:
    # Get the photo information sent by the user
    photo = update.message.photo[-1]  # Assuming the last photo is the largest
    photo_id = photo.file_id

    # Store the photo file_id in user_data
    context.user_data["photo_id"] = photo_id

    # Provide feedback to the user about the received photo
    await update.message.reply_text(
        f"Thank you for sharing your selfie photo!\n"
        "You can share more information or press 'Done' to finish the conversation.",
        reply_markup=markup_photo,
    )

    # Transition to the ADDITIONAL_INFO state
    return CHOOSING


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the gathered info and end the conversation."""
    user_data = context.user_data
    await update.message.reply_text(
        f"I have collected the following information:\n"
        f"Phone Number: {user_data.get('phone_number', 'Not provided')}\n"
        f"Location: {user_data.get('location', 'Not provided')}\n"
        f"Additional Information: {user_data.get('additional_info', 'Not provided')}\n"
        "Thank you! If you need further assistance, feel free to ask."
    )

    user_data.clear()
    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE, and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [
                MessageHandler(filters._Contact(), received_phone_number),
                MessageHandler(filters.PHOTO, received_photo),
                MessageHandler(filters._Location(), received_location),
            ],
            TYPING_CHOICE: [
                MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), received_photo),
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Done$"), done)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
