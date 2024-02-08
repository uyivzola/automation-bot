import logging
import os

from openpyxl.worksheet.filters import Filters
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardButton, InlineKeyboardMarkup, \
    KeyboardButton
from telegram.ext import (Application, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters,
                          CallbackContext, Updater)
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
BOT_USERNAME = os.getenv('BOT_USERNAME')

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger('httpx').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

GENDER, PHOTO, LOCATION, PHONE_NUMBER, DELPHI_LOGIN, DELPHI_PASSWORD = range(6)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ Starts the conversation and ask the user about their gender"""
    reply_keyboard = [['Boy', 'Girl', 'Other']]
    # reply_keyboard_inline = [[InlineKeyboardButton('Boy', callback_data=print('pressed 1'))]]
    # reply_keyboard_inline_markup = InlineKeyboardMarkup(reply_keyboard_inline)

    reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder="Qanaqasan?")
    await update.message.reply_text("HI! My name is Professor Behzod Khidirov! I will hold a conversation with you! "
                                    "Are you Boy or a girl?", reply_markup=reply_markup)
    return GENDER


async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores selected gender and asks for a photo of the user"""
    user = update.message.from_user.first_name
    gender = update.message.text

    logger.info("Gender of %s: %s", user, gender)
    context.user_data['gender'] = gender
    await update.message.reply_text(
        "I see! Please send me a photo of yourself..."
        "so I know what you look like", reply_markup=ReplyKeyboardRemove(),
    )

    return PHOTO


location_reply_keyboard = [
    [KeyboardButton("Send Location 📍", request_location=True)]
]
location_markup = ReplyKeyboardMarkup(location_reply_keyboard, one_time_keyboard=True,
                                      input_field_placeholder='Manzilingizni kiriting.')


async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the photo and asks for a location."""
    user = update.message.from_user
    picture = update.message.photo[-1]  # Assuming the last photo is the largest
    picture_id = picture.file_id
    photo_file = await update.message.photo[-1].get_file()
    context.user_data['picture_id'] = picture_id

    await photo_file.download_to_drive(f'{user.first_name}s photo.jpg')

    logger.info("Photo of %s: %s", user.first_name, "photo is stored as it is")
    await update.message.reply_text("you are so cute!"
                                    "please give me your location", reply_markup=location_markup)
    return LOCATION


phone_reply_keyboard = [
    [KeyboardButton("Send Phone Number ☎️", request_contact=True)]
]

phone_markup = ReplyKeyboardMarkup(phone_reply_keyboard, one_time_keyboard=True,
                                   input_field_placeholder='Telefon raqamingizni yuboring')


async def location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the location and asks for phone number info about the user"""
    user = update.message.from_user
    user_location = update.message.location
    latitude, longitude = user_location.latitude, user_location.longitude

    # Assuming your chat_id is stored in the variable 'chat_id'
    chat_id = update.message.chat_id
    context.user_data["location"] = f"Latitude: {latitude}, Longitude: {longitude}"
    logger.info("Contact of %s: %s", user.first_name, user_location)

    await update.message.reply_text(f"Thanks for sharing your location! {context.user_data['location']}"
                                    f"Now I need your phone number!", reply_markup=phone_markup)

    return PHONE_NUMBER


async def phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the phone number and asks for user his/her login to Delphi"""
    user = update.message.from_user
    contact = update.message.contact
    context.user_data["phone_number"] = contact
    logger.info("Contact of %s: %s", user.first_name, contact)

    await update.message.reply_text(f"Good. Please enter your login to DELPHI: ", reply_markup=ReplyKeyboardRemove()
                                    )
    return DELPHI_LOGIN


async def delphi_login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the Delphi login and asks for user his/her PASSWORD to Delphi"""
    user = update.message.from_user
    message_id = update.message.message_id
    context.user_data["login"] = update.message.text
    await update.message.reply_text(f"Good user with login: {update.message.text}"
                                    f"Please enter your password:")
    logger.info("Login of %s: %s", user.first_name, update.message.text)

    return DELPHI_PASSWORD


async def delphi_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the Delphi Password and asks for user his/her shit"""
    user = update.message.from_user
    chat_id = update.message.chat_id
    message_id = update.message.message_id
    password = update.message.text
    if update.message.chat.type != 'private':
        await update.message.reply_text('Please send your password in a private chat for security.')
        return ConversationHandler.END

    # Store the password securely in the user_data
    context.user_data["password"] = password

    # Delete the password message from the user's perspective
    await context.bot.deleteMessage(chat_id=chat_id, message_id=message_id)

    # Perform further actions based on your application's logic
    # PASSWORD IS HERE and it is stored as password

    await update.message.reply_text('See you soon! Good bye!')

    logger.info("Password of %s: %s", user.first_name, update.message.text)
    await update.message.reply_text('Password received. Processing your request securely 🔐')
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation with the user"""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text("Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def main() -> None:
    """RUN THE BOT"""
    # Create the Application and pass it your bot's token

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add conversation handler with the states GENDER, PHOTO, LOCATION, PHONE_NUMBER, DELPHI_LOGIN, DELPHI_PASSWORD

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            GENDER: [MessageHandler(filters.Regex("^(Boy|Girl|Other$)"), gender)],
            PHOTO: [MessageHandler(filters.PHOTO, photo)],
            LOCATION: [MessageHandler(filters._Location(), location)],
            PHONE_NUMBER: [MessageHandler(filters._Contact(), phone_number)],
            DELPHI_LOGIN: [MessageHandler(filters.TEXT, delphi_login)],
            DELPHI_PASSWORD: [MessageHandler(filters.TEXT, delphi_password)]
        }, fallbacks=[CommandHandler("cancel", cancel)]
    )

    application.add_handler(conv_handler)
    # Run the bot until the user presses CTRL - C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
