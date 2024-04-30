import os
import time
from itertools import islice

import pandas as pd
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, filters, CommandHandler, ContextTypes, MessageHandler
import logging

from dotenv import load_dotenv
from sqlalchemy import create_engine

env_file_path = 'D:/Projects/.env'
load_dotenv(env_file_path)

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

last_processed_data = None

# Telegram bot token and group chat ID
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN3')
GLOBAL_SLEEP_DURATION = 600
amount = 1000000
invoice_min_amount = 5_000_000
sql_query = f"""
select i.Number      as InvoiceNumber,
       D.Name        as DocKind,
       C.FindName    as ClientName,
       PCM.Name      as ClientManager,
       G.Name        as GoodName,
       P.Name        as ProducerName,
       il.kolich     as Quantity,
       il.pSumma     as ProductTotalAmount,
       i.DataEntered as DataEntered
from INVOICE I
         join CLIENT C on I.ClientId = C.ClientId
         join invoiceln il on il.InvoiceId = i.InvoiceId
         join PERSONAL PCM on C.PersonalId = PCM.PersonalId
         join IncomeLn incl on il.IncomeLnId = incl.IncomeLnId
         join Good G on incl.GoodId = G.GoodId
         join PRODUCER P on G.ProducerId = P.ProducerId
         join DocKind D on I.DocKindId = D.DocKindId
where (D.Name in (N'Оптовая реализация',
                  N'Финансовая скидка'))
  and i.pSumma > {amount}
  and CONVERT(date, i.DataEntered) = CONVERT(date, GETDATE()) -- today's data
order by i.DataEntered
"""


def load_data_from_excel() -> pd.DataFrame:
    ##################### ACCESS ENV VARIABLES ######################
    db_server = os.getenv("DB_SERVER")
    db_database = os.getenv("DB_DATABASE_SERGELI")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_port = os.getenv("DB_PORT")
    db_driver_name = os.getenv("DB_DRIVER_NAME")

    conn_str = f"mssql+pyodbc://{db_user}:{db_password}@{db_server}:{db_port}/{db_database}?driver={db_driver_name}"
    engine = create_engine(conn_str)

    # df = pd.read_excel('./minutely.xlsx')
    df = pd.read_sql_query(sql_query, engine)
    print(df.shape)
    return df


async def check_for_updates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    chat_id = update.message.chat_id
    global last_processed_data

    current_data = load_data_from_excel()

    if last_processed_data is None:
        last_processed_data = current_data
        return False

    new_invoices = current_data[~current_data.isin(last_processed_data)].dropna()
    if not new_invoices.empty:
        if 'InvoiceNumber' in new_invoices.columns:  # Check if 'InvoiceNumber' column exists
            for invoice_number, invoice_group in new_invoices.groupby('InvoiceNumber'):
                # Calculate the total amount of the invoice
                invoice_total_amount = invoice_group['ProductTotalAmount'].sum()

                # Construct the message based on the invoice total amount
                if invoice_total_amount >= invoice_min_amount:
                    message = (f"💊 <b>Новая отгрузка!</b>\n\n"
                               f"📝 Номер фактуры: {invoice_number}\n"
                               f"📎 Тип документа: <b>{invoice_group['DocKind'].iloc[0]}</b>\n"
                               f"🕛 Дата отгрузки: <i>{invoice_group['DataEntered'].iloc[0]}</i>\n\n"
                               f"👨‍💼 Менеджер: <b>{invoice_group['ClientManager'].iloc[0]}</b>\n"
                               f"👥 Название клиента: <b>{invoice_group['ClientName'].iloc[0]}</b>\n"
                               f"<b>💰 Общая Сумма: <u>{invoice_total_amount:,.0f} сум</u></b>\n"
                               f"<b>➖➖➖➖➖➖➖➖➖➖➖</b>\n\n"
                               f"<b>Товары:</b>\n")
                    # Fetch details of goods from the invoice
                    for _, good_row in islice(invoice_group.iterrows(), 10):
                        message += (f"📦 Товар: <b>{good_row['GoodName']}</b>\n"
                                    f"🏭 Производитель: {good_row['ProducerName']}\n"
                                    f"🔢 Количество: {good_row['Quantity']:,.0f}\n"
                                    f"💰 Сумма товара: {good_row['ProductTotalAmount']:,.0f} сум\n\n")
                else:
                    message = (f"💊 <b>Новая отгрузка!</b>\n\n"
                               f"📝 Номер фактуры: {invoice_number}\n"
                               f"📎 Тип документа: <b>{invoice_group['DocKind'].iloc[0]}</b>\n"
                               f"🕛 Дата отгрузки: <i>{invoice_group['DataEntered'].iloc[0]}</i>\n\n"
                               f"👨‍💼 Менеджер: <b>{invoice_group['ClientManager'].iloc[0]}</b>\n"
                               f"👥 Название клиента: <b>{invoice_group['ClientName'].iloc[0]}</b>\n"
                               f"<b>💰 Общая Сумма: <u>{invoice_total_amount:,.0f} сум</u></b>")

                await context.bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.HTML)
                time.sleep(1)
            last_processed_data = pd.concat([last_processed_data, new_invoices], ignore_index=True)
            return True
        else:
            logging.warning("InvoiceNumber column not found in new_invoices DataFrame")
            return False
    else:
        return False


# These usually take the two arguments update and context.
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
    application.add_handler(CommandHandler('start', start))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
