import os
from datetime import datetime

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import logging

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID")


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Print user information and command to the terminal
    user = update.effective_user
    user_name = user.username
    user_id = user.id

    if context.args:
        command = context.args[0]  # Assuming the command is passed as an argument
        print(f"User Name: {user_name}, User ID: {user_id}, Command: {command}")
    else:
        print(f"User Name: {user_name}, User ID: {user_id}, No command specified")

    await update.message.reply_text(f'Hello {user.first_name}')


def log_user_message(user, message):
    # Get current timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Format the log message
    log_message = f'{timestamp} - User: {user.username}, Message: {message}\n'

    # Write the log message to a file
    with open('log.txt', 'a') as log_file:
        log_file.write(log_message)


async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    message_text = update.message.text

    # Log the user message
    log_user_message(user, message_text)

    # Check if the message contains a file (photo, document, etc.)
    if update.message.document or update.message.photo:
        # Save the file to the 'media' folder
        media_folder = 'media'
        os.makedirs(media_folder, exist_ok=True)

        if update.message.document:
            await update.message.document.get_file()
        elif update.message.photo:
            await update.message.photo[-1].get_file()

        await update.message.reply_text(f'Thank you for the file! It has been saved in the "media" folder.')


async def start(update, context):
    user = update.message.from_user
    username = user.first_name

    today_date = datetime.now().strftime('%d %b')
    file_name = f'LIMIT - {today_date}.xlsx'
    chat_id = update.message.chat_id

    # Send a preliminary message
    message = await update.message.reply_text("Sizning so'rovingiz bo'yicha fayl tayyorlanmoqda😎. "
                                              "Iltimos kuting...")

    try:

        # limit_generator()
        # Check the modification time of the file
        modification_time = datetime.fromtimestamp(os.path.getmtime(file_name))

        # Open and send the document
        document = open(file_name, 'rb')
        await context.bot.send_document(chat_id, document,
                                        caption=f"Savdoyingizga baraka tilayman🤲🏼, Hurmatli {username}!😻\n \n\n"
                                                f"Ushbu fayl {modification_time.strftime('%d-%B, soat %H:%M')} da "
                                                f"yangilangan.")

        # Delete the preliminary message
        await message.delete()

        # Send a final message
        spoiler_text = ("|| Bu bot test rejimida ishlamoqda\!"
                        " Xatolar bo\'lsa to\'g\'ri tushunasiz degan umiddaman😊 ||")

        await update.message.reply_text(spoiler_text, parse_mode='MarkdownV2')
    except Exception as e:
        # Handle exceptions and reply with an error message
        error_message = f'Error sending the file: {str(e)}'
        print(error_message)
        await update.message.reply_text(error_message)


app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

app.add_handler(CommandHandler("hello", hello))
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.ALL & ~ filters.COMMAND, handle_messages))

app.run_polling()
