import os, re, time, logging, requests
from itertools import islice

import pandas as pd
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, filters, CommandHandler, ContextTypes, MessageHandler
from minutely_bot import check_for_updates
from bs4 import BeautifulSoup

from dotenv import load_dotenv
from sqlalchemy import create_engine

env_file_path = 'D:/Projects/.env'
load_dotenv(env_file_path)

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

last_processed_data = None

# Telegram bot token and group chat ID
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN3')
GLOBAL_SLEEP_DURATION = 900
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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""

    user = update.message.from_user.first_name
    await update.message.reply_html(
        rf"Hi {user}! You look beautiful today!",
    )


async def sale_hunter(update, context=ContextTypes.DEFAULT_TYPE) -> bool:
    await update.message.reply_text('🍗 Sales hunter is started...')
    # while True:
    #     await check_for_updates(update, context)
    #     time.sleep(GLOBAL_SLEEP_DURATION


URL = "https://fom.uz/en/org"
# Create a folder to store downloaded files
folder_path = "price_lists_companies"

if not os.path.exists(folder_path):
    os.makedirs(folder_path)


async def sanitize_filename(filename: str) -> str:
    # Remove 'OOO' (three consecutive 'O' characters)
    filename = re.sub(r'OOO', '', filename)
    # Replace invalid characters with underscores
    invalid_chars = r'[<>:"\'/%\\|?*]'
    sanitized_filename = re.sub(invalid_chars, '', filename)
    return sanitized_filename


async def extract_data_from_page(url, update: Update, context=ContextTypes.DEFAULT_TYPE):
    try:
        # Send HTTP request
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        if response.status_code == 200:
            html_content = response.text
            # Parse HTML content
            soup = BeautifulSoup(html_content, "html.parser")
            # Find all company blocks
            company_blocks = soup.find_all("div", class_="block company-list")
            # Loop through each company block
            for company_block in company_blocks:

                # Extract company details
                company_name: str = company_block.find("div", class_="title").text.strip()
                company_name = await sanitize_filename(company_name)

                phone_number_tag = company_block.find("div", class_="call").find("a")
                if phone_number_tag:
                    phone_number = phone_number_tag["href"].split(":")[-1]
                else:
                    phone_number = "Not available"

                # Check if the download link exists
                download_link_tag = company_block.find("div", class_="price").find("a")

                if download_link_tag:
                    download_link = download_link_tag["href"]
                    file_extension = os.path.splitext(download_link)[1]
                    # Download price file
                    price_response = requests.get(download_link)
                    if price_response.status_code == 200:
                        filename = f"{company_name}{file_extension}"
                        with open(os.path.join(folder_path, filename), "wb") as f:
                            f.write(price_response.content)
                        logging.info(f"{filename} is given to bot as url")
                        await context.bot.send_document(chat_id=update.message.chat_id,
                                                        document=open(os.path.join(folder_path, filename), "rb"),
                                                        caption=f'{company_name}\n\n'
                                                                f'☎️ {phone_number}')
                        time.sleep(4)
                else:
                    print(f"No download link found for {company_name}")
            # Find next page link if exists
            next_page_link = soup.find("li", class_="next").find("a")
            if next_page_link:
                # Remove the duplicated "/en/org" part from the next page URL
                next_page_url = url.split("/en/org")[0] + next_page_link["href"]
                await extract_data_from_page(url=next_page_url, update=update, context=context)
        else:
            print(f"Failed to retrieve data from the page: {url}")
    except (requests.RequestException, ValueError) as error:
        logging.error(f"Error fetching data from {url}: {error}")
        # Handle the error gracefully


async def all_companies_prices(update: Update, context=ContextTypes.DEFAULT_TYPE) -> bool:
    initial_message = await update.message.reply_text(
        text='Fetching data from the websites...⌛\nThis might take a while, please be patient.'
    )
    try:
        await extract_data_from_page(url=URL, update=update, context=context)
    except Exception as e:
        logging.error(f"Error in fetching all companies prices: {e}")
        await update.message.reply_text("An error occurred while fetching data. Please try again later.")
    finally:
        await initial_message.delete()


def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Start command handler
    application.add_handler(CommandHandler('start', start))
    # application.add_handler(CommandHandler('sale_hunter', sale_hunter))
    application.add_handler(CommandHandler('price', all_companies_prices))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
