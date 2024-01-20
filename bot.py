# -*- coding: UTF-8 -*-
import os
from datetime import datetime

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

from reports.limit import limit_generator
from reports.oxvat import oxvat_generator
from reports.top import top_generator

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME")


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


def handle_response(text: str) -> str:
    processed: str = text.lower()

    if 'hello' in processed:
        return 'Hello there!'

    if 'how are you' in processed:
        return 'Remember to subscribe!'


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text: str = update.message.text
    user = update.message.from_user

    # Log the user message
    log_user_message(user, message_text)

    print(f'User:({update.message.chat.id}, {user}) - "{message_text}"')

    if 'limit' in message_text.lower():
        await limit(update, context)
    if 'top' in message_text.lower():
        await top(update, context)
    if 'oxvat' in message_text.lower():
        await oxvat(update, context)
    if 'start' in message_text.lower():
        await started(update, context)
    else:
        response: str = handle_response(message_text)
        print('Bot:', response)
        await update.message.reply_text(response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


# Sends LIMIT CLIENTS
async def limit(update, context):
    user = update.message.from_user
    username = user.first_name

    today_date = datetime.now().strftime('%d %b')
    file_name = f'LIMIT - {today_date}.xlsx'
    chat_id = update.message.chat_id

    # Send a preliminary message
    message = await update.message.reply_text(
        f"Sizning so\'rovingiz bo\'yicha  \n *LIMIT \- {today_date}\.xlsx* \n fayl tayyorlanmoqda😎 "
        "Iltimos kuting⌛⌛⌛ \(o\'rtacha 5 daqiqa\)", parse_mode='MarkdownV2')

    try:

        limit_generator()
        # Check the modification time of the file
        modification_time = datetime.fromtimestamp(os.path.getmtime(file_name))

        # Open and send the document
        document = open(file_name, 'rb')
        await context.bot.send_document(chat_id, document,
                                        caption=f"Savdoyingizga baraka tilayman🤲🏼💸, Hurmatli {username}!😻\n \n\n"
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


# Sends TOP OSTATOK TOVAROV
async def top(update, context):
    user = update.message.from_user
    username = user.first_name

    today_date = datetime.now().strftime('%d %b')
    file_name = f'TOP ostatok - {today_date}.xlsx'
    chat_id = update.message.chat_id

    # Send a preliminary message
    message = await update.message.reply_text(
        f"Sizning so\'rovingiz bo\'yicha \n *TOP ostatok \- {today_date}\.xlsx* \nfayl tayyorlanmoqda😎 "
        "Iltimos kuting⌛\(o\'rtacha 3 daqiqa\)", parse_mode='MarkdownV2')

    try:

        top_generator()
        # Check the modification time of the file
        modification_time = datetime.fromtimestamp(os.path.getmtime(file_name))

        # Open and send the document
        document = open(file_name, 'rb')
        await context.bot.send_document(chat_id, document,
                                        caption=f"Asklepiy Distribution Skladidagi Tovarlar ro'yxati📑. \n Charchamang, {username}!😉\n \n\n"
                                                f"Ushbu fayl {modification_time.strftime('%d-%B, soat %H:%M')}da "
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


# OXVAT RUN sends oxvachenniye klienti!
async def oxvat(update, context):
    user = update.message.from_user
    username = user.first_name

    today_date = datetime.now().strftime('%d %b')
    file_name = f'NE OXVACHEN - {today_date}.xlsx'
    chat_id = update.message.chat_id

    # Send a preliminary message
    message = await update.message.reply_text(
        f"Sizning so\'rovingiz bo\'yicha \n  *NE OXVACHEN \- {today_date}\.xlsx*  \n fayl tayyorlanmoqda😎 "
        "Iltimos kuting⌛⌛⌛\(o\'rtacha 5 daqiqa\)", parse_mode='MarkdownV2')

    try:

        oxvat_generator()
        # Check the modification time of the file
        modification_time = datetime.fromtimestamp(os.path.getmtime(file_name))

        # Open and send the document
        document = open(file_name, 'rb')
        await context.bot.send_document(chat_id, document,
                                        caption=f"Yangi mijozlar bilan xushmomila bo'ling🙈\n \n\n"
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


## Starting text where it will welcome the users and introduce what this bot can do.
async def started(update, context):
    user = update.message.from_user
    username = user.first_name

    today_date = datetime.now().strftime('%d %b')

    # Send a preliminary message
    message = await update.message.reply_text(f"""
Assalomu alaykum! Mening botimga xush kelibsiz, {username}!
Ushbu bot sizga LIMIT | OXVAT | TOP ostatok kabi ro'yxatlarni yuboradi.

Sizga bot tomonidan fayl kelmagunigacha ozroq kuting. ⏳🔁 (o'rtacha 5 daqiqa)

Shunchaki quyidagilarni yozing📈:
- oxvat yoki /oxvat
- limit yoki /limit
- top yoki /top

Qo'llab quvvatlasangiz, juda ham hursand bo'laman!🥰

Hurmat bilan Behzod🖤 . 

Murojaat uchun @hopxol
""")


if __name__ == '__main__':
    print('🤖 Starting bot...')
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Commands
    app.add_handler(CommandHandler("start", started))

    app.add_handler(CommandHandler("limit", limit))
    app.add_handler(CommandHandler("top", top))
    app.add_handler(CommandHandler("oxvat", oxvat))

    # Error handler
    app.add_error_handler(error)

    # Polls the bot
    print('Polling...')
    app.run_polling(poll_interval=1)
