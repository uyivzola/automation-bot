import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, ContextTypes
from telegram.ext import CallbackContext
from calendar import monthrange
from dotenv import load_dotenv

# Define conversation states
START, END, YEAR, MONTH, DAY, MENU = range(6)

# Dictionary to store user's selections
user_data = {}

env_file_path = 'D:/Projects/.env'
load_dotenv(env_file_path)
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')


# Start function
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [[InlineKeyboardButton("Start Year", callback_data='start_year'),
                 InlineKeyboardButton("Start Month", callback_data='start_month'),
                 InlineKeyboardButton("Start Day", callback_data='start_day')],
                [InlineKeyboardButton("End Year", callback_data='end_year'),
                 InlineKeyboardButton("End Month", callback_data='end_month'),
                 InlineKeyboardButton("End Day", callback_data='end_day')],
                [InlineKeyboardButton("Cancel", callback_data='cancel')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Please choose:', reply_markup=reply_markup)

    return MENU


# Callback query handler
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Store user's selection
    user_data[query.data] = query.data

    if query.data in ['start_year', 'end_year']:
        context.user_data['state'] = YEAR
        keyboard = [[InlineKeyboardButton("2022", callback_data='2022'),
                     InlineKeyboardButton("2023", callback_data='2023'),
                     InlineKeyboardButton("2024", callback_data='2024')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Please choose a year:", reply_markup=reply_markup)
    elif query.data in ['start_month', 'end_month']:
        context.user_data['state'] = MONTH
        keyboard = [[InlineKeyboardButton("January", callback_data='1'),
                     InlineKeyboardButton("February", callback_data='2'),
                     InlineKeyboardButton("March", callback_data='3'),
                     InlineKeyboardButton("April", callback_data='4'),
                     InlineKeyboardButton("May", callback_data='5'),
                     InlineKeyboardButton("June", callback_data='6')],
                    [InlineKeyboardButton("July", callback_data='7'),
                     InlineKeyboardButton("August", callback_data='8'),
                     InlineKeyboardButton("September", callback_data='9'),
                     InlineKeyboardButton("October", callback_data='10'),
                     InlineKeyboardButton("November", callback_data='11'),
                     InlineKeyboardButton("December", callback_data='12')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Please choose a month:", reply_markup=reply_markup)
    elif query.data in ['start_day', 'end_day']:
        context.user_data['state'] = DAY

        selected_year = int(context.user_data.get('year'))
        selected_month = int(context.user_data.get('month'))
        days_in_month = monthrange(int(selected_year), selected_month)[-1]

        # For simplicity, let's assume 31 days for all months
        keyboard = [[InlineKeyboardButton(str(day), callback_data=str(day)) for day in range(1, days_in_month + 1)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Please choose a day:", reply_markup=reply_markup)
    elif query.data == 'cancel':
        await query.edit_message_text(text="Cancelled.")
        return ConversationHandler.END


# Function to handle unknown commands
async def unknown(update, context):
    await update.message.reply_text("Sorry, I didn't understand that command.")


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(text="Hello World!")


def main() -> None:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    # application.add_handler(CommandHandler('hello', hello))

    # Define conversation handler with the states
    # conv_handler = ConversationHandler(
    #     entry_points=[CommandHandler('start', start)],
    #     states={
    #         MENU: [CallbackQueryHandler(button)],
    #         YEAR: [CallbackQueryHandler(button)],
    #         MONTH: [CallbackQueryHandler(button)],
    #         DAY: [CallbackQueryHandler(button)],
    #     },
    #     fallbacks=[CommandHandler('cancel', unknown)], per_message=True
    # )
    #
    # application.add_handler(conv_handler)
    # application.add_error_handler(error)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
