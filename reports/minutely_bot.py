import os
import time

import pandas as pd
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, filters, CommandHandler, ContextTypes, MessageHandler
import logging

from dotenv import load_dotenv

env_file_path = 'D:/Projects/.env'
load_dotenv(env_file_path)

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

last_processed_data = None

# Telegram bot token and group chat ID
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN3')
GLOBAL_SLEEP_DURATION = 10
amount = 10_000_000

sql_query = f"""
select i.Number      as InvoiceNumber,
       D.Name        as DocKind,
       C.Inn         as INN,
       C.FindName    as ClientName,
       PCM.Name      as ClientManager,
       i.pSumma      as TotalAmount,
       i.DataEntered as DataEntered
from INVOICE I
         join CLIENT C on I.ClientId = C.ClientId
         join PERSONAL PCM on C.PersonalId = PCM.PersonalId
         join DocKind D on I.DocKindId = D.DocKindId
where (D.Name in (N'Возврат товара от покупателя',
                  N'Оптовая реализация',
                  N'Финансовая скидка'))
  and i.pSumma > {amount}
  and CONVERT(date, i.DataEntered) = CONVERT(date, GETDATE()) -- today's data
order by i.DataEntered
"""


def load_data_from_excel() -> pd.DataFrame:
    df = pd.read_excel('./minutely.xlsx')
    return df


async def check_for_updates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    global last_processed_data

    current_data = load_data_from_excel()

    if last_processed_data is None:
        last_processed_data = current_data
        return False

    new_invoices = current_data[~current_data.isin(last_processed_data)].dropna()
    if not new_invoices.empty:
        for _, row in new_invoices.iterrows():
            message = (f"🚀 <b>Новая отгрузка!</b>\n\n"
                       f"📝 Номер фактуры: {row['InvoiceNumber']:.0f}\n"
                       f"📎 Тип документа: <b>{row['DocKind']}</b>\n"
                       # f"👤 ИНН: {row['INN']:.0f}\n"
                       f"🕛 Дата отгрузки: <i>{row['DataEntered']}</i>\n\n"
                       f"👨‍💼 Менеджер: <b>{row['ClientManager']}</b>\n"
                       f"👥 Название клиента: <b>{row['ClientName']}</b>\n"
                       f"<b>💰 Сумма: <u>{row['TotalAmount']:,.0f} сум</u></b>")

            await context.bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.HTML)
            time.sleep(1)
        last_processed_data = pd.concat([last_processed_data, new_invoices], ignore_index=True)
        return True
    else:
        return False


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""

    user = update.message.from_user.name
    await update.message.reply_html(
        rf"Hi {user}! You look beautiful today!😁",
    )
    print(f'{user} started the bot.')
    while True:
        await check_for_updates(update, context)
        time.sleep(GLOBAL_SLEEP_DURATION)


def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Start command handler
    application.add_handler(MessageHandler(filters.TEXT, start))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
