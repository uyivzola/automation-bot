import os
import re
import time
import logging
import requests
import pandas as pd
from itertools import islice
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, filters, CommandHandler, ContextTypes, MessageHandler
from minutely_bot import check_for_updates
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from sqlalchemy import create_engine

# from reports.date_selector import select_period, period_conv_handler

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

company_info = []  # List to store company information

# SQL query to fetch invoice data
sql_query = f"""
    SELECT i.Number AS InvoiceNumber,
           D.Name AS DocKind,
           C.FindName AS ClientName,
           PCM.Name AS ClientManager,
           G.Name AS GoodName,
           P.Name AS ProducerName,
           il.kolich AS Quantity,
           il.pSumma AS ProductTotalAmount,
           i.DataEntered AS DataEntered
    FROM INVOICE I
             JOIN CLIENT C ON I.ClientId = C.ClientId
             JOIN invoiceln il ON il.InvoiceId = i.InvoiceId
             JOIN PERSONAL PCM ON C.PersonalId = PCM.PersonalId
             JOIN IncomeLn incl ON il.IncomeLnId = incl.IncomeLnId
             JOIN Good G ON incl.GoodId = G.GoodId
             JOIN PRODUCER P ON G.ProducerId = P.ProducerId
             JOIN DocKind D ON I.DocKindId = D.DocKindId
    WHERE (D.Name IN (N'Оптовая реализация',
                      N'Финансовая скидка'))
      AND i.pSumma > {amount}
      AND CONVERT(date, i.DataEntered) = CONVERT(date, GETDATE()) -- today's data
    ORDER BY i.DataEntered
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

                company_info.append({'Company Name': company_name, 'Phone Number': phone_number})
                print(company_info)

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
        # Save collected company information to Excel file
        save_company_info_to_excel()
    except Exception as e:
        logging.error(f"Error in fetching all companies prices: {e}")
        await update.message.reply_text("An error occurred while fetching data. Please try again later.")
    finally:
        await initial_message.delete()


def save_company_info_to_excel():
    # Create a DataFrame from the collected company information
    df = pd.DataFrame(company_info)
    # Save the DataFrame to Excel
    excel_file_path = 'company_info.xlsx'
    df.to_excel(excel_file_path, index=False)
    logging.info(f"Company information saved to {excel_file_path}")


def scrape_product_info(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extracting product name
    product_name = soup.find('div', class_='product-card__title').text.strip()

    # Extracting specifications
    specifications = soup.find_all('div', class_='product-card__specifications-row')
    product_data = {'Title': product_name}
    for spec in specifications:
        name = spec.find(class_='product-card__specifications-name').text.strip().rstrip(':')
        value = spec.find(class_='product-card__specifications-value').text.strip()
        product_data[name] = value

    # Extracting product description
    description = soup.find('div', class_='product-card__use-text')
    description_text = description.text.strip() if description else "Description not available"

    # Extracting image source
    image_source_tag = soup.find('a', class_='product-for__item')
    image_source = image_source_tag['href'] if image_source_tag else "Image not available"

    # Handling the case of preloader.gif
    if 'preloader.gif' in image_source:
        image_source = 'Image not available'

    # Adding image source to product data
    product_data['Image Source'] = image_source

    # Adding description to product data
    product_data['Description'] = description_text

    return product_data


def scrape_product_urls(main_url):
    response = requests.get(main_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    product_urls = [a['href'] for a in soup.find_all('a', class_='product__footer')]
    return product_urls


async def products_info_updater(update: Update, context=ContextTypes.DEFAULT_TYPE) -> bool:
    await update.message.reply_text('🛒 Updating product information...')

    try:
        # Scrape product URLs
        main_url = 'https://kusum.uz/products/?postsperpage=115'
        product_urls = scrape_product_urls(main_url)

        for url in product_urls:
            product_info = scrape_product_info(url)
            # Send product information along with image
            await send_product_info(update, context, product_info)
            # Delay between sending each product info
            time.sleep(4)

    except Exception as e:
        logging.error(f"Error in updating product information: {e}")
        await update.message.reply_text("An error occurred while updating product information. Please try again later.")


async def send_product_info(update: Update, context, product_info):
    try:
        # Extract image source
        image_source = product_info.pop('Image Source', 'Image not available')
        # Send image
        product_info_message = "\n".join([f"{key.strip()}: {value}" for key, value in product_info.items()])[:1000]
        await context.bot.send_photo(chat_id=update.message.chat_id, photo=image_source, caption=product_info_message)
        # Send product information
        # await update.message.reply_text(product_info_message)

    except Exception as e:
        logging.error(f"Error in sending product information: {e}")
        await update.message.reply_text("An error occurred while sending product information.")


def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Start command handler
    application.add_handler(CommandHandler('start', start))
    # application.add_handler(period_conv_handler)
    # application.add_handler(CommandHandler('sale_hunter', sale_hunter))
    application.add_handler(CommandHandler('price', all_companies_prices))
    application.add_handler(CommandHandler('products_info_updater', products_info_updater))
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
