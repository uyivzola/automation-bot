# buttons.py
import logging.config
import os
import random
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup
from telegram.constants import ParseMode

from reports.date_selector import date_selection_required
from reports.gulya_jokes import gulya_opa_jokes
from reports.hourly import hourly_generator
from reports.limit import limit_generator
from reports.monthly import monthly_generator
from reports.okm import okm_generator
from reports.oxvat import oxvat_generator
from reports.planned_actual_sales import planned_actual_sales_generator
from reports.to_finskidka import to_finskidka_generator
from reports.top import top_generator
from reports.top_products_sold import top_product_sold_generator
from reports.weather import weather

logging.config.fileConfig('config/logging_config.ini')
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

logger = logging.getLogger(__name__)


async def chuck_norris_jokes(update, context):
    message_id = update.message.message_id
    message_text = update.message.text
    message = await update.message.reply_text(f"i am thinking about the joke about {message_text}",
                                              reply_to_message_id=message_id)
    try:
        req = requests.get("https://api.chucknorris.io/jokes/random", verify=False)

        if req.status_code == 200:
            # Parse the JSON response
            response_json = req.json()

            text = response_json["value"]
            # Print the extracted text VALUE
            print(text)
            bot_response = await message.edit_text(text)  # await update.message.delete()
            await context.bot.pin_chat_message(chat_id=update.message.chat_id, message_id=bot_response.message_id)


        else:
            # Print an error message if the request was not successful
            await message.delete()
            print(f"Error: {req.status_code}")
            await update.message.reply_text(f"{req.status_code}", reply_to_message_id=message_id)
    except Exception as e:
        # Handle exceptions and reply with an error message
        error_message = f'Error sending the file: {str(e)}'
        print(error_message)
        await update.message.reply_text(error_message, reply_to_message_id=message_id)


async def gulya_jokes(update, context):
    message_id = update.message.message_id
    message_text = update.message.text
    message = await update.message.reply_text(f"i am thinking about the joke about {message_text}",
                                              reply_to_message_id=message_id)
    try:
        joke = random.choice(gulya_opa_jokes)
        if joke:
            # time.sleep(1)
            # await message.delete()
            # time.sleep(1)
            await message.edit_text(joke)
            print(joke)
        else:
            await message.delete(message_id)
            await update.message.reply_text("Sorry, I couldn't find any joke :(", reply_to_message_id=message_id)
    except Exception as e:
        # Handle exceptions and reply with an error message
        error_message = f'Error sending the file: {str(e)}'
        print(error_message)
        await update.message.reply_text(error_message, reply_to_message_id=message_id)


async def oxvat(update, context):
    chat_id = update.message.chat_id
    message_id = update.message.message_id

    today_date = datetime.now().strftime('%d %b')
    file_name = f'NE OXVACHEN - {today_date}.xlsx'
    login = context.user_data.get("login", "")
    password = context.user_data.get("password", "")

    # Send a preliminary message
    message = await update.message.reply_text(f'<b>NE OXVACHEN - {today_date}.xlsx</b>\n\nfayl tayyorlanmoqda😎\n\n'
                                              'Iltimos kuting⌛⌛⌛(Maksimum 3 daqiqa)', parse_mode='HTML',
                                              reply_to_message_id=message_id)
    try:
        oxvat_generator(login, password)

        modification_time = datetime.fromtimestamp(os.path.getmtime(file_name))
        current_time = datetime.now()
        time_difference = current_time - modification_time

        # Open and send the document
        with open(file_name, 'rb') as document:
            await context.bot.send_document(chat_id, document,
                                            caption=f"\n\n\n🔁Updated: {modification_time.strftime('%d %B, %H:%M')}",
                                            reply_to_message_id=message_id)
        await message.delete()
    except Exception as e:
        # Handle exceptions and reply with an error message
        error_message = f'Error sending the file: {str(e)}'
        await update.message.reply_text(error_message, reply_to_message_id=message_id)
        logging.error(error_message)


async def top(update, context):
    if update.callback_query:
        chat_id = update.callback_query.message.chat_id
        message_id = update.callback_query.message.message_id
    else:
        chat_id = update.message.chat_id
        message_id = update.message.message_id

    personal_name = context.user_data.get("personal_name", "")

    today_date = datetime.now().strftime('%d %b')

    current_directory = os.getcwd()
    files_in_directory = os.listdir(current_directory)

    # Send a preliminary message
    message = await update.message.reply_text(
        f"Hurmatli <b>{personal_name}</b>, Sizning so\'rovingiz bo\'yicha\n"
        f"<b>TOP OSTATOK.xlsx</b> \n fayl tayyorlanmoqda😎\n\n"
        "Iltimos kuting⌛⌛⌛ (o\'rtacha 5 daqiqa)", parse_mode='HTML', reply_to_message_id=message_id)

    logging.info(f'Started processing {top.__name__} request for user: {personal_name}')

    try:
        # Open and send the document
        logging.info(f'Calling {top_generator.__name__} function.')

        top_generator()
        file_names = [file for file in files_in_directory if file.startswith("TOP ostatok")]

        logging.info(f'Completed {top_generator.__name__} function.')

        for file_name in file_names:
            # Check if the file was modified more than 2 hours ago

            with open(file_name, 'rb') as document:
                logging.info(f'Sending file {document} to chat {chat_id}.')
                await context.bot.send_document(chat_id, document, reply_to_message_id=message_id)

            logging.info(f'Deleting {file_name}')
            os.remove(file_name)

        logging.info('Deleting preliminary message.')
        await message.delete()
    except Exception as e:
        # Handle exceptions and reply with an error message
        error_message = f'Error sending the file: {str(e)}'
        await update.message.reply_text(error_message, reply_to_message_id=message_id)
        logging.error(error_message)

    logging.info(f'Finished processing {top.__name__} request for user: {personal_name}')


async def limit(update, context):
    message_id = update.message.message_id

    today_date = datetime.now().strftime('%d %b')
    file_name = f'LIMIT - {today_date}.xlsx'
    chat_id = update.message.chat_id

    login = context.user_data.get("login", "")
    password = context.user_data.get("password", "")
    personal_name = context.user_data.get("personal_name", "")

    # Send a preliminary message
    message = await update.message.reply_text(
        f"Hurmatli <b>{personal_name}</b>, Sizning so\'rovingiz bo\'yicha\n<b>{file_name}</b> \n fayl tayyorlanmoqda😎\n\n"
        "Iltimos kuting⌛⌛⌛ (o\'rtacha 5 daqiqa)", parse_mode='HTML', reply_to_message_id=message_id)

    logging.info(f'Started processing {limit.__name__} request for user: {personal_name}')
    try:
        logging.info('Calling limit_generator function.')
        limit_generator(login, password, context)
        logging.info(f'Opening file {file_name}.')

        with open(file_name, 'rb') as document:
            logging.info(f'Sending file {document} to chat {chat_id}.')
            await context.bot.send_document(chat_id, document, reply_to_message_id=message_id)

        # Delete the preliminary message
        await message.delete()  # await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        # Handle exceptions and reply with an error message
        error_message = f'Error sending the file: {str(e)}'
        await update.message.reply_text(error_message, reply_to_message_id=message_id)
        logging.error(error_message)

    logging.info(f'Finished processing {limit.__name__} request for user: {personal_name} (Login: {login}).')


async def currency(update, context):
    message_id = update.message.message_id

    # Send a GET request to the website
    url = 'https://bank.uz/uz/currency'
    response = requests.get(url)

    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    # Extract "Sotish" (sell) data
    sell_data = soup.find('div', class_='bc-inner-blocks-right').find_all('div', class_='bc-inner-block-left-texts')

    # Extract "Sotib olish" (buy) data
    buy_data = soup.find('div', class_='bc-inner-block-left').find_all('div', class_='bc-inner-block-left-texts')

    # Prepare the message content
    message = "<b>Sotish (Sell)</b>               <b>Sotib olish (Buy)</b>\n"
    message += "<b>Bank Name</b>      <b>Rate</b>              <b>Bank Name</b>      <b>Rate</b>\n"

    # Print the extracted data
    print(f"{'Sotish':<30}{'Sotib olish'}")
    print(f"{'Bank Name':<25}{'Rate':<15}{'Bank Name':<25}{'Rate'}")
    for sell, buy in zip(sell_data, buy_data):
        sell_bank_name = sell.find('span', class_='medium-text').text.strip()
        sell_rate = sell.find('span', class_='medium-text green-date').text.strip()
        buy_bank_name = buy.find('span', class_='medium-text').text.strip()
        buy_rate = buy.find('span', class_='medium-text green-date').text.strip()
        message += f"{sell_bank_name:<25}{sell_rate:<15}{buy_bank_name:<25}{buy_rate}\n"

        print(f"{sell_bank_name:<25}{sell_rate:<15}{buy_bank_name:<25}{buy_rate}")

    await update.message.reply_text(reply_to_message_id=message_id, text=message, parse_mode=ParseMode.HTML)


async def hourly(update, context):
    user = update.message.from_user
    first_name = user.first_name
    message_id = update.message.message_id

    login = context.user_data.get("login", "")
    password = context.user_data.get("password", "")

    today_date = datetime.now().strftime('%d %b')
    file_name = f'HOURLY.xlsx'
    chat_id = update.message.chat_id

    # Send a preliminary message
    message = await update.message.reply_text(f"<b>{file_name}</b> \n fayl tayyorlanmoqda😎 \n\n"
                                              "Iltimos kuting⌛⌛⌛ (Maksimum 3 daqiqa)", parse_mode='HTML',
                                              reply_to_message_id=message_id)
    try:
        hourly_generator(login, password)
        logging.info(f'Opening file {file_name}.')
        with open(file_name, 'rb') as document:
            await context.bot.send_document(chat_id, document,
                                            # caption=f"Analitikangizga aniqlik tilayman!📈, {first_name}💋💖!\n \n\n",
                                            # f"🔁Updated: {modification_time.strftime('%d %B,%H:%M')}",
                                            reply_to_message_id=message_id)

        await message.delete()
        os.remove(file_name)
        logging.info(f'File {file_name} deleted.')

    except Exception as e:
        # Handle exceptions and reply with an error message
        error_message = f'Error sending or deleting the file: {str(e)}'
        logging.error(error_message)
        await update.message.reply_text(error_message, reply_to_message_id=message_id)


async def okm(update, context):
    user = update.message.from_user
    first_name = user.first_name
    message_id = update.message.message_id

    login = context.user_data.get("login", "")
    password = context.user_data.get("password", "")

    today_date = datetime.now().strftime('%d %b : %H:%M')
    file_name = f'ГАТ.xlsx'
    chat_id = update.message.chat_id

    # Send a preliminary message
    message = await update.message.reply_text(f"{file_name} at {today_date}\n fayl tayyorlanmoqda😎 \n\n"
                                              "Iltimos kuting⌛⌛⌛(Maksimum 3 daqiqa)", parse_mode='HTML',
                                              reply_to_message_id=message_id)
    try:
        logging.info(f'Start running {okm_generator.__name__}')
        okm_generator()

        logging.info(f'Opening file {file_name}.')
        with open(file_name, 'rb') as document:
            await context.bot.send_document(chat_id, document,
                                            reply_to_message_id=message_id,
                                            caption=f'ГАТ - Гинокапс, Ацекард, Тризим\n\n'
                                                    f'Updated: {today_date}')

        await message.delete()
        os.remove(file_name)
        logging.info(f'File {file_name} deleted.')

    except Exception as e:
        # Handle exceptions and reply with an error message
        error_message = f'Error sending the file: {str(e)}'
        await update.message.reply_text(error_message, reply_to_message_id=message_id)
        logging.error(error_message)


async def planned_actual_sales(update, context) -> None:
    user = update.message.from_user
    first_name = user.first_name
    message_id = update.message.message_id

    yesterday = (datetime.now() - timedelta(days=1)).strftime('%d %B')
    output_file_path = f'PLANNED - ACTUAL SALES - {yesterday}.xlsx'
    chat_id = update.message.chat_id
    # Send a preliminary message
    message = await update.message.reply_text(f"<b>PLANNED ACTUAL SALES for {yesterday}.xlsx</b> is coming...",
                                              parse_mode='HTML',
                                              reply_to_message_id=message_id)
    try:
        logging.info(f'Creating {output_file_path}...')
        planned_actual_sales_generator(output_file_path)

        logging.info(f'Opening file {output_file_path}.')
        with open(output_file_path, 'rb') as document:
            await context.bot.send_document(chat_id, document,
                                            reply_to_message_id=message_id,
                                            caption=f'PLANNED ACTUAL SALES for {yesterday}')
        await message.delete()
        os.remove(output_file_path)
        logging.info(f'File {output_file_path} deleted.')
    except Exception as e:

        error_message = f'Error sending the file: {str(e)}'
        await update.message.reply_text(error_message, reply_to_message_id=message_id)
        logging.error(error_message)


@date_selection_required
async def to_finskidka(update, context):
    logging.info('Start To Finskidka')

    selected_dates = context.user_data.get('selected_dates')
    if not selected_dates:
        await update.message.reply_text('Please select the dates first.')
        return

    start_date = selected_dates["start_date"]
    end_date = selected_dates["end_date"]
    logging.info(f'Selected dates: {start_date} - {end_date}')
    if update.callback_query:
        chat_id = update.callback_query.message.chat_id
        message_id = update.callback_query.message.message_id
    else:
        chat_id = update.message.chat_id
        message_id = update.message.message_id

    # Send a preliminary message
    message = await context.bot.send_message(
        chat_id,
        f"Data for {start_date} to {end_date} is being prepared.\n\nBe Patient!",
        reply_to_message_id=message_id
    )
    try:
        logging.info('Start generating To Finskidka')
        file_name = to_finskidka_generator(start_date=start_date, end_date=end_date)
        logging.info('ENDED generating To Finskidka')

        modification_time = datetime.fromtimestamp(os.path.getmtime(file_name))

        with open(file_name, 'rb') as document:
            await context.bot.send_document(chat_id, document,
                                            caption=f"Period: From {start_date} -> {end_date} 📈\n\n\n"
                                                    f"🔁Updated: {modification_time.strftime('%Y. %d %B,%H:%M')}",
                                            reply_to_message_id=message_id)
            await message.delete()

    except Exception as e:
        # Handle exceptions and reply with an error message
        error_message = f'Error sending the file: {str(e)}'
        await update.callback_query.message.reply_text(error_message, reply_to_message_id=message_id)
        logging.error(error_message)


async def monthly(update, context):
    chat_id = update.message.chat_id
    message_id = update.message.message_id

    CURRENT_MONTH = datetime.now().month
    CURRENT_YEAR = datetime.now().year

    start_date = datetime(CURRENT_YEAR, CURRENT_MONTH, 1).strftime('%Y%m%d')
    end_date = datetime(CURRENT_YEAR, CURRENT_MONTH, datetime.now().day + 1).strftime('%Y%m%d')

    # Send a preliminary message
    message = await update.message.reply_text(f"Be Patient. I am working on it",
                                              reply_to_message_id=message_id)

    try:
        file_name = monthly_generator(current_month=True, start_date=start_date, end_date=end_date)

        modification_time = datetime.fromtimestamp(os.path.getmtime(file_name))
        current_time = datetime.now()

        # Open and send the document
        with open(file_name, 'rb') as document:
            await context.bot.send_document(chat_id, document,
                                            caption=f"Period: From {start_date} -> {end_date} 📈\n\n\n"
                                                    f"🔁Updated: {modification_time.strftime('%Y. %d %B,%H:%M')}",
                                            reply_to_message_id=message_id)
        await message.delete()

    except Exception as e:
        # Handle exceptions and reply with an error message
        error_message = f'Error sending the file: {str(e)}'
        print(error_message)
        await update.message.reply_text(error_message, reply_to_message_id=message_id)


@date_selection_required
async def past_monthly(update, context):
    selected_dates = context.user_data.get('selected_dates')

    if not selected_dates:
        await update.message.reply_text("Please select the dates first.")
        return

    start_date = selected_dates['start_date']
    end_date = selected_dates['end_date']
    if update.callback_query:
        chat_id = update.callback_query.message.chat_id
        message_id = update.callback_query.message.message_id
    else:
        chat_id = update.message.chat_id
        message_id = update.message.message_id

    # Send a preliminary message
    message = await context.bot.send_message(
        chat_id,
        f"Data for {start_date} to {end_date} is being prepared.\n\nBe Patient!",
        reply_to_message_id=message_id
    )
    try:
        file_name = monthly_generator(current_month=False, start_date=start_date, end_date=end_date)

        modification_time = datetime.fromtimestamp(os.path.getmtime(file_name))
        current_time = datetime.now()

        # Open and send the document
        with open(file_name, 'rb') as document:
            await context.bot.send_document(chat_id, document,
                                            caption=f"Period: From {start_date} -> {end_date} 📈\n\n\n"
                                                    f"🔁Updated: {modification_time.strftime('%Y. %d %B,%H:%M')}",
                                            reply_to_message_id=message_id)
        await message.delete()

    except Exception as e:
        # Handle exceptions and reply with an error message
        error_message = f'Error sending the file: {str(e)}'
        logging.error(error_message)
        await update.callback_query.message.reply_text(error_message, reply_to_message_id=message_id)


@date_selection_required
async def top_high_fav(update, context):
    selected_dates = context.user_data.get('selected_dates')

    if not selected_dates:
        await update.message.reply_text("Please select the dates first.")
        return

    start_date = selected_dates['start_date']
    end_date = selected_dates['end_date']

    selected_dates = context.user_data.get('selected_dates')

    if not selected_dates:
        await update.message.reply_text("Please select the dates first.")
        return

    start_date = selected_dates['start_date']
    end_date = selected_dates['end_date']
    if update.callback_query:
        chat_id = update.callback_query.message.chat_id
        message_id = update.callback_query.message.message_id
    else:
        chat_id = update.message.chat_id
        message_id = update.message.message_id

    # Send a preliminary message
    message = await context.bot.send_message(
        chat_id,
        f"Data for {start_date} to {end_date} is being prepared.\n\nBe Patient!",
        reply_to_message_id=message_id
    )

    try:
        logging.info(f'Top High Fav: {start_date} to {end_date}')
        top_files = top_product_sold_generator(start_date=start_date, end_date=end_date)
        logging.info(f'OUTSIDE: {start_date} to {end_date}')

        for function_name, file_data in top_files.items():
            file_name = file_data['file_name']
            file_desc = file_data['description']
            picture_name = file_data['picture_name']
            # Open and send the document
            modification_time = datetime.fromtimestamp(os.path.getmtime(file_name))
            with open(file_name, 'rb') as document:

                caption_text = (f"{file_desc}\n\n"
                                f"Period: From <b><u>{start_date} -> {end_date} 📈</u></b>\n\n\n"
                                f"🔁Updated: {modification_time.strftime('%Y. %d %B,%H:%M')}")

                main_file_message = await context.bot.send_document(chat_id, document, caption=caption_text,
                                                                    parse_mode='HTML', reply_to_message_id=message_id)
                # try:
                #     for subtype in ['ROZ', 'Сеть']:
                #         picture_file_path = f'reports/trash_media/Top_20_Goods_{file_name.split("-")[1].split("_")[0]}_{subtype}.png'
                #         with open(picture_file_path, 'rb') as picture:
                #             if os.path.exists(picture_file_path):
                #                 await context.bot.send_photo(chat_id, photo=picture,
                #                                              caption=f'ТОП 20 {file_desc} - {subtype}',
                #                                              reply_to_message_id=main_file_message.message_id)
                #         # os.remove(picture_file_path)
                # except Exception as e:
                #     logging.error(e)
        await message.delete()
    except Exception as e:
        # Handle exceptions and reply with an error message
        error_message = f'Error sending the file: {str(e)}'
        logging.error(error_message)
        await update.message.reply_text(error_message, reply_to_message_id=message_id)


async def delete_xlsx_files(update, context) -> None:
    # Get the chat ID and user ID for logging purposes
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    first_name = update.message.from_user.first_name

    # Specify the directory where you want to delete '*.xlsx' files
    directory_paths = ['./', 'price_lists_companies']

    try:
        # Iterate through files in the directory and try to delete '*.png' files with names longer than 11 characters
        for directory_path in directory_paths:
            for filename in os.listdir(directory_path):
                for file_extensions in ['.xlsx', '.csv', '.xls']:
                    if filename.endswith(file_extensions):
                        file_path = os.path.join(directory_path, filename)
                        try:
                            os.remove(file_path)
                            logger.info(f'{first_name} deleted {file_path}')
                            # await update.message.reply_text(f'{filename} has been deleted successfully!')
                        except Exception as e:
                            # Log any errors that may occur during the file deletion process
                            error_message = f"Error deleting {filename}: {str(e)}"
                            await context.bot.send_message(chat_id=chat_id, text=error_message)

        # Notify the user about the completion of the deletion process
        await update.message.reply_text('Excel files have been deleted successfully!')
    except Exception as e:
        # Log any errors that may occur during the file iteration process
        error_message = f"Error iterating through files: {str(e)}"
        await context.bot.send_message(chat_id=chat_id, text=error_message)


async def delete_png_files(update, context) -> None:
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id

    # Specify the directory where you want to delete '*.xlsx' files
    directory_path = './reports/trash_media/'

    try:
        # Iterate through files in the directory and try to delete '*.xlsx' files
        for filename in os.listdir(directory_path):
            if filename.endswith(".png") and len(filename) > 11:
                file_path = os.path.join(directory_path, filename)
                try:
                    os.remove(file_path)
                    # msg = await update.message.reply_text(f'{filename} has been deleted successfully!')
                    # await msg.delete()
                except Exception as e:
                    # Log any errors that may occur during the file deletion process
                    error_message = f"Error deleting {filename}: {str(e)}"
                    await context.bot.send_message(chat_id=chat_id, text=error_message)

        # Notify the user about the completion of the deletion process
        await update.message.reply_text('All files have been deleted successfully!')
    except Exception as e:
        # Log any errors that may occur during the file iteration process
        error_message = f"Error iterating through files: {str(e)}"
        await context.bot.send_message(chat_id=chat_id, text=error_message)


button_functions = {
    'FINSKIDKA📈': to_finskidka,
    '️Past Monthly': past_monthly,
    'LIMIT💸': limit,
    '💵 kurs': currency,
    'OXVAT🙈': oxvat,
    'TOP OSTATOK🔄️': top,
    '🔝 TOP | FAV | HIGH SOLD': top_high_fav,
    "ГАТ": okm,
    "PLANNED | ACTUAL SALES": planned_actual_sales,
    'HOURLY⏳': hourly,
    '️Current Month️️': monthly,
    'WEATHER❄️☀️ for today': weather,
    'Jokes about Gulya😅': gulya_jokes,
    '🤠 Chuck Norris Jokes 😁': chuck_norris_jokes,
    '🗑️ Clear Files': delete_xlsx_files,
    '🖼️ Delete PNG': delete_png_files
}
