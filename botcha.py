import logging
# -*- coding: UTF-8 -*-
import os
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import create_engine
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler, \
    CallbackContext

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
user_photos = 'reports/trash_media/user_photos'

POSITION, PHOTO, PHONE_NUMBER, DELPHI_LOGIN, DELPHI_PASSWORD, REPORTS = range(6)


def log_user_message(user, message):
    # Get current timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Format the log message
    log_message = (f'{timestamp} - UserID: {user.id}, '
                   f'User: {user.username}, '
                   f'First Name: {user.first_name}, '
                   f'Message: {message}\n')

    # Write the log message to a file
    with open('log.txt', 'a', encoding='utf-8') as log_file:
        log_file.write(log_message)
    print(log_message)


def check_database_access(username, password) -> bool:
    # Load environment variables
    env_file_path = 'D:/Projects/.env'
    load_dotenv(env_file_path)
    db_server = os.getenv("DB_SERVER")
    db_database = os.getenv("DB_DATABASE_SERGELI")
    db_port = os.getenv("DB_PORT")
    db_driver_name = os.getenv("DB_DRIVER_NAME")

    # Construct the connection string
    conn_str = f"mssql+pyodbc://{username}:{password}@{db_server}:{db_port}/{db_database}?driver={db_driver_name}"
    print(username, password)
    try:
        # Attempt to connect to the database
        engine = create_engine(conn_str)
        connection = engine.connect()
        connection.close()
        return True
    except Exception as e:
        print(f"Connection failed: {str(e)}")
        return False


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ Starts the conversation and ask the user about their gender"""
    reply_keyboard = [['Regional Director🔝', 'Sales Manager💬', 'BOSS🔥']]

    reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder="Qanaqasan?")
    await update.message.reply_text("HI! Professor Behzod Khidirov! I will hold a conversation with you! "
                                    "Are you Regional Director or a Sales Manager?", reply_markup=reply_markup)
    return POSITION


async def position(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores selected gender and asks for a photo of the user"""
    chat_id = update.message.chat_id
    message_id = update.message.message_id

    user = update.message.from_user.first_name
    gender = update.message.text

    logger.info("Gender of %s: %s", user, gender)
    context.user_data['gender'] = gender
    await context.bot.send_photo(chat_id, photo='reports/trash_media/user_photos/sample_photo.jpg',
                                 caption=f'Iltimos o\'zingizning rasmingizni quyidagicha ko\'rinishda yuboring',
                                 reply_to_message_id=message_id, reply_markup=ReplyKeyboardRemove())
    return PHOTO


phone_reply_keyboard = [
    [KeyboardButton("Send Phone Number ☎️", request_contact=True)]
]
phone_markup = ReplyKeyboardMarkup(phone_reply_keyboard, one_time_keyboard=True,
                                   input_field_placeholder='Telefon raqamingizni yuboring')


async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the photo and asks for a location."""
    user = update.message.from_user
    picture = update.message.photo[-1]  # Assuming the last photo is the largest
    picture_id = picture.file_id
    photo_file = await update.message.photo[-1].get_file()
    context.user_data['picture_id'] = picture_id
    await photo_file.download_to_drive(f'{user_photos}/{user.first_name}s_photo.jpg')

    logger.info("Photo of %s: %s", user.first_name, "photo is stored as it is")
    await update.message.reply_text("you are so cute!"
                                    "please give me your location", reply_markup=phone_markup)
    return PHONE_NUMBER


async def phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the phone number and asks for user his/her login to Delphi"""
    user = update.message.from_user
    contact = update.message.contact
    context.user_data["phone_number"] = contact
    logger.info("Contact of %s: %s", user.first_name, contact)

    login = await update.message.reply_text(f"Delphi LOGIN kiriting 👀: ", reply_markup=ReplyKeyboardRemove())
    return DELPHI_LOGIN


async def delphi_login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the Delphi login and asks for user his/her PASSWORD to Delphi"""
    user = update.message.from_user
    message_id = update.message.message_id
    context.user_data["login"] = update.message.text

    password = await update.message.reply_text(f"Sizning loginingiz {update.message.text} /n/n"
                                               f"Parolingizni kiriting:")
    logger.info("Login of %s: %s", user.first_name, update.message.text)

    return DELPHI_PASSWORD


async def delphi_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the Delphi Password and asks for user his/her access"""
    user = update.message.from_user
    chat_id = update.message.chat_id
    message_id = update.message.message_id
    password = update.message.text

    if update.message.chat.type != 'private':
        await update.message.reply_text('Please send your password in a private chat for security.')
        return ConversationHandler.END

    # Store the password securely in the user_data
    context.user_data["login"] = context.user_data.get("login", "")
    context.user_data["password"] = password

    # Delete the password message from the user's perspective
    await context.bot.deleteMessage(chat_id=chat_id, message_id=message_id)

    logger.info("Password of %s: %s", user.first_name, update.message.text)
    await update.message.reply_text('Sizning Bazaga dostupingizni tekshirayapman. Kuting... 🔐')
    print(context.user_data["login"], context.user_data["password"])
    has_access = check_database_access(username=context.user_data["login"], password=context.user_data["password"])

    if has_access:
        # await update.message.reply_text('Connection is on its way...', reply_to_message_id=message_id)
        await context.bot.send_message(text='Congrats! Now Press BUTTONS👇🏼', chat_id=chat_id, reply_markup=buttons)
        return REPORTS
    else:
        await update.message.reply_text('NOTOGRI! Qayta Tekshiring')
        return DELPHI_LOGIN


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation with the user"""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text("Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


async def button_handler(update: Update, context: CallbackContext) -> None:
    button_text = update.message.text
    message_text: str = update.message.text
    user = update.message.from_user
    login = context.user_data.get("login", "")
    password = context.user_data.get("password", "")

    # Use the button_functions dictionary to get the corresponding function
    button_function = button_functions.get(button_text)
    log_user_message(user, message_text)

    if button_function:
        await button_function(update, context)
    else:
        # Handle the case where the button text doesn't match any function
        await update.message.reply_text(f"No function defined for button: {button_text}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bots token.
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            POSITION: [MessageHandler(filters.Regex("^(Regional Director🔝|Sales Manager💬|BOSS🔥$)"), position)],
            PHOTO: [MessageHandler(filters.PHOTO, photo)],
            # LOCATION: [MessageHandler(filters._Location(), location)],
            PHONE_NUMBER: [MessageHandler(filters._Contact(), phone_number)],
            DELPHI_LOGIN: [MessageHandler(filters.TEXT, delphi_login)],
            DELPHI_PASSWORD: [MessageHandler(filters.TEXT, delphi_password)],
            REPORTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler)]
        }, fallbacks=[CommandHandler("cancel", cancel)]
    )

    # on different commands - answer in Telegram
    # application.add_handler(CommandHandler("start", start, block=False))
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command, block=False))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
