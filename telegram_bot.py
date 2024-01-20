from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes, ApplicationBuilder, CommandHandler, filters, MessageHandler

TELEGRAM_BOT_TOKEN = '6637240694:AAHF674z1_LPBcdtd8j9P2LQS-SduikYOtc'
BOT_USERNAME = 'behzodKtelegrambot'


def log_user_message(user, message):
    # Get current timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Format the log message
    log_message = f'{timestamp} - User: {user.username}, Message: {message}\n'

    # Write the log message to a file
    with open('log.txt', 'a') as log_file:
        log_file.write(log_message)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! Thanks for chatting with me! I am a banana!')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('This is help command')


async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('THIS IS CUSTOM COMMAND')


# Responses


def handle_response(text: str) -> str:

    processed: str = text.lower()
    if 'hello' in processed:
        return 'Hello there!'

    if 'how are you' in processed:
        return 'Remember to subscribe!'

    return 'I dont understand what you wrote!('


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    message_text: str = update.message.text
    user = update.message.from_user

    # Log the user message
    log_user_message(user, message_text)

    print(f'User:({update.message.chat.id}, {user}) in {message_type}:"{message_text}"')

    if message_type == 'group':
        if BOT_USERNAME in message_text:
            new_text: str = message_text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)

        else:
            return
    else:
        response: str = handle_response(message_text)
    print('Bot:', response)
    await update.message.reply_text(response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


if __name__ == '__main__':
    print('🤖 Starting bot...')
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # COMMANDS
    app.add_handler(CommandHandler("start", start_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # ERROR
    app.add_error_handler(error)
    # Polls the bot
    print('Polling...')
    app.run_polling(poll_interval=3)
