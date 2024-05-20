import logging
from datetime import datetime
from functools import wraps

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackQueryHandler,
    ConversationHandler, ContextTypes, CallbackContext,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Define the states
START_PERIOD, START_YEAR, SELECT_START_MONTH, SELECT_START_DAY, SELECT_END_MONTH, SELECT_END_DAY = range(6)

years = [2022, 2023, 2024]  # List of years
years_keyboard = [
    [InlineKeyboardButton(year, callback_data=year) for year in years]
]

months = ['January', 'February', 'March', 'April',
          'May', 'June', 'July', 'August', 'September',
          'October', 'November', 'December']

months_keyboard = [
    [InlineKeyboardButton(month, callback_data=month) for month in months[i:i + 2]] for i in
    range(0, len(months), 2)
]

days = [day for day in range(1, 32)]
days_keyboard = [
    [InlineKeyboardButton(day, callback_data=day) for day in days[i:i + 4]] for i in range(0, len(days), 4)
]


def date_selection_required(func):
    @wraps(func)
    async def wrapper(update, context: CallbackContext):
        context.user_data['next_function'] = func
        context.user_data['callback_function'] = func

        await select_period(update, context)
        return ConversationHandler.END

    return wrapper


async def select_period(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message is None:
        logger.error("No message associated with the update.")
        return ConversationHandler.END

    keyboard = [
        [
            InlineKeyboardButton("📅 Select Period", callback_data='PERIOD')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Lets Select Period:", reply_markup=reply_markup)
    return START_PERIOD


async def select_year(update, context):
    query = update.callback_query
    await query.answer()
    reply_markup = InlineKeyboardMarkup(years_keyboard)
    await query.edit_message_text(text="Please select a year:", reply_markup=reply_markup)
    # await update.message.reply_text(text="Please select a year:", reply_markup=reply_markup)
    # Next state after year selection
    return START_YEAR


async def select_start_month(update, context):
    """Select the start month."""
    query = update.callback_query
    await query.answer()
    context.user_data['year'] = int(query.data)
    selected_year = context.user_data['year']
    reply_markup = InlineKeyboardMarkup(months_keyboard)
    await query.edit_message_text(text=f"Year: <b>{selected_year}</b>\n"
                                       "Please select a start month:", reply_markup=reply_markup, parse_mode='HTML')
    return SELECT_START_MONTH


async def select_start_day(update, context):
    """Select the starting day."""
    query = update.callback_query
    await query.answer()
    context.user_data['start_month'] = query.data
    selected_year = context.user_data['year']
    selected_start_month = context.user_data['start_month']
    reply_markup = InlineKeyboardMarkup(days_keyboard)
    await query.edit_message_text(text=f"Year: <b>{selected_year}</b>\n"
                                       f"Start Month: <b>{selected_start_month}</b>\n"
                                       f"Please select the starting day:", reply_markup=reply_markup,
                                  parse_mode='HTML')
    return SELECT_START_DAY


async def select_end_month(update, context):
    """Select the end month."""
    query = update.callback_query
    await query.answer()
    context.user_data['start_day'] = query.data
    selected_year = context.user_data['year']
    selected_start_month = context.user_data['start_month']
    selected_start_day = context.user_data['start_day']

    start_index = months.index(selected_start_month)
    filtered_months = months[start_index:]

    filtered_months_keyboard = [
        [InlineKeyboardButton(month, callback_data=month) for month in filtered_months[i:i + 2]] for i in
        range(0, len(filtered_months), 2)
    ]
    reply_markup = InlineKeyboardMarkup(filtered_months_keyboard)

    await query.edit_message_text(text=f"Year: <b>{selected_year}</b>\n"
                                       f"Start Month:<b>{selected_start_month}</b>\n"
                                       f"Start Day: <b>{selected_start_day}</b>\n"
                                       f"Please select the END month:", reply_markup=reply_markup,
                                  parse_mode='HTML')
    return SELECT_END_MONTH


async def select_end_day(update, context):
    """Select the ending day."""
    query = update.callback_query
    await query.answer()
    context.user_data['end_month'] = query.data
    selected_year = context.user_data['year']
    selected_start_month = context.user_data['start_month']
    selected_start_day = context.user_data['start_day']
    selected_end_month = context.user_data['end_month']
    reply_markup = InlineKeyboardMarkup(days_keyboard)
    await query.edit_message_text(text=f"Year: <b>{selected_year}</b>\n"
                                       f"Start Month: <b>{selected_start_month}</b>\n"
                                       f"Start Day: <b>{selected_start_day}</b>\n"
                                       f"End Month: <b>{selected_end_month}</b>\n"
                                       f"Please select the END day:", reply_markup=reply_markup, parse_mode='HTML')
    return SELECT_END_DAY


async def end(update, context):
    query = update.callback_query
    await query.answer()
    context.user_data['end_day'] = query.data
    selected_year = context.user_data['year']
    selected_start_month = context.user_data['start_month']
    selected_start_day = context.user_data['start_day']
    selected_end_month = context.user_data['end_month']
    selected_end_day = context.user_data['end_day']

    await query.edit_message_text(text=f"Year: <b>{selected_year}</b>\n"
                                       f"Start Month: <b>{selected_start_month}</b>\n"
                                       f"Start Day: <b>{selected_start_day}</b>\n"
                                       f"End Month: <b>{selected_end_month}</b>\n"
                                       f"End Day: <b>{selected_end_day}</b>\n\n",
                                  parse_mode='HTML')

    start_date = datetime.strptime(f"{selected_year}{selected_start_month}{selected_start_day}",
                                   '%Y%B%d').date().strftime('%Y%m%d')
    end_date = datetime.strptime(f"{selected_year}{selected_end_month}{selected_end_day}", '%Y%B%d').date().strftime(
        '%Y%m%d')

    # Store selected dates in context.user_data
    context.user_data['selected_dates'] = {
        'start_date': start_date,
        'end_date': end_date
    }

    callback_function = context.user_data.get('callback_function')
    if callback_function:
        await callback_function(update, context)
    else:
        await query.edit_message_text(text="No callback function found.")

    return ConversationHandler.END


async def cancel(update, context):
    """Cancel the conversation."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="The conversation was canceled.")
    return ConversationHandler.END


period_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(select_year)],
    states={
        START_PERIOD: [CallbackQueryHandler(select_year)],
        START_YEAR: [CallbackQueryHandler(select_start_month)],
        SELECT_START_MONTH: [CallbackQueryHandler(select_start_day)],
        SELECT_START_DAY: [CallbackQueryHandler(select_end_month)],
        SELECT_END_MONTH: [CallbackQueryHandler(select_end_day)],
        SELECT_END_DAY: [CallbackQueryHandler(end)],
    },
    fallbacks=[CallbackQueryHandler(cancel)], per_message=True
)
