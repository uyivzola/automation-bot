# buttons.py
import os
import random
from datetime import datetime, timedelta

import requests

from reports.gulya_jokes import gulya_opa_jokes
from reports.hourly import hourly_generator
from reports.limit import limit_generator
from reports.montly import monthly_generator
from reports.oxvat import oxvat_generator
from reports.to_finskidka import to_finskidka_generator
from reports.top import top_generator
from reports.top_products_sold import top_product_sold_generator


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
    message = await update.message.reply_text(f'*NE OXVACHEN \- {today_date}\.xlsx*\n\nfayl tayyorlanmoqda😎\n\n'
                                              '||Iltimos kuting⌛⌛⌛\(Maksimum 3 daqiqa\)||', parse_mode='MarkdownV2',
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
        print(error_message)
        await update.message.reply_text(error_message, reply_to_message_id=message_id)


async def top(update, context):
    chat_id = update.message.chat_id
    message_id = update.message.message_id

    login = context.user_data.get("login", "")
    password = context.user_data.get("password", "")
    personal_name = context.user_data.get("personal_name", "")

    today_date = datetime.now().strftime('%d %b')
    file_names = [f'TOP ostatok - {today_date}.xlsx', f'TOP ostatok - Эвер-Ромфарм  - {today_date}.xlsx']
    # Send a preliminary message
    message = await update.message.reply_text(
        f"Hurmatli {personal_name},Sizning so\'rovingiz bo\'yicha \n *TOP ostatok \- {today_date}\.xlsx* \nfayl tayyorlanmoqda😎 "
        "Iltimos kuting⌛\(Maksimum 3 daqiqa\)", parse_mode='MarkdownV2', reply_to_message_id=message_id)
    try:
        # Open and send the document
        for file in file_names:
            if not os.path.exists(file):
                top_generator(login, password)
            # Check the modification time of the file
            modification_time = datetime.fromtimestamp(os.path.getmtime(file))

            # Current time
            current_time = datetime.now()

            # Check if the file was modified more than 2 hours ago
            time_difference = current_time - modification_time
            if time_difference >= timedelta(minutes=1):
                top_generator(login, password)

            with open(file, 'rb') as document:
                print(f'Sending {file}')
                await context.bot.send_document(chat_id, document, reply_to_message_id=message_id)

        await message.delete()

    except Exception as e:
        # Handle exceptions and reply with an error message
        error_message = f'Error sending the file: {str(e)}'
        print(error_message)
        await update.message.reply_text(error_message, reply_to_message_id=message_id)


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
        f"Hurmatli *{personal_name}*, Sizning so\'rovingiz bo\'yicha  \n *LIMIT \- {today_date}\.xlsx* \n fayl tayyorlanmoqda😎 "
        "Iltimos kuting⌛⌛⌛ \(o\'rtacha 5 daqiqa\)", parse_mode='MarkdownV2', reply_to_message_id=message_id)

    try:
        limit_generator(login, password, context)

        # Open and send the document
        with open(file_name, 'rb') as document:
            await context.bot.send_document(chat_id, document, reply_to_message_id=message_id)

        # Delete the preliminary message
        await message.delete()  # await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        # Handle exceptions and reply with an error message
        error_message = f'Error sending the file: {str(e)}'
        print(error_message)
        await update.message.reply_text(error_message, reply_to_message_id=message_id)


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
    message = await update.message.reply_text(f"*HOURLY \- {today_date}\.xlsx* \n fayl tayyorlanmoqda😎 \n\n"
                                              "||Iltimos kuting⌛⌛⌛\(Maksimum 3 daqiqa\)||", parse_mode='MarkdownV2',
                                              reply_to_message_id=message_id)

    try:
        if not os.path.exists(file_name):
            hourly_generator(login, password)

        modification_time = datetime.fromtimestamp(os.path.getmtime(file_name))
        current_time = datetime.now()
        time_difference = current_time - modification_time

        if time_difference >= timedelta(hours=2):
            hourly_generator(login, password)
        # Open and send the document
        with open(file_name, 'rb') as document:
            await context.bot.send_document(chat_id, document,
                                            caption=f"Analitikangizga aniqlik tilayman!📈, {first_name}💋💖!\n \n\n"
                                                    f"🔁Updated: {modification_time.strftime('%d %B,%H:%M')}",
                                            reply_to_message_id=message_id)
        await message.delete()  # Send a final message

    except Exception as e:
        # Handle exceptions and reply with an error message
        error_message = f'Error sending the file: {str(e)}'
        print(error_message)
        await update.message.reply_text(error_message, reply_to_message_id=message_id)


async def to_finskidka(update, context):
    user = update.message.from_user
    username = user.first_name
    message_id = update.message.message_id

    login = context.user_data.get("login", "")
    password = context.user_data.get("password", "")
    today_date = datetime.now().strftime('%d %b')
    file_name = f'TOandFinSkidka.xlsx'
    chat_id = update.message.chat_id

    # Send a preliminary message
    message = await update.message.reply_text(f"*TOandFinSkidka \- {today_date}\.xlsx* \n fayl tayyorlanmoqda😎 \n\n"
                                              "||Iltimos kuting⌛⌛⌛\(Maksimum 3 daqiqa\)||", parse_mode='MarkdownV2',
                                              reply_to_message_id=message_id)

    try:
        if not os.path.exists(file_name):
            to_finskidka_generator(login, password)

        modification_time = datetime.fromtimestamp(os.path.getmtime(file_name))
        current_time = datetime.now()
        time_difference = current_time - modification_time

        if time_difference >= timedelta(hours=2):
            print(f'i am running {to_finskidka_generator.__name__}')
            to_finskidka_generator(login, password)

        # Open and send the document
        with open(file_name, 'rb') as document:

            await context.bot.send_document(chat_id, document,
                                            caption=f"Analitikangizga aniqlik tilayman!📈, {username}!\n \n\n"
                                                    f"🔁Updated: {modification_time.strftime('%d %B,%H:%M')}",
                                            reply_to_message_id=message_id)

        await message.delete()  # Delete preliminary message
    except Exception as e:
        # Handle exceptions and reply with an error message
        error_message = f'Error sending the file: {str(e)}'
        print(error_message)
        await update.message.reply_text(error_message, reply_to_message_id=message_id)


async def monthly(update, context):
    today_date = datetime.now().strftime('%d %b')
    file_name = f'MONTHLY.xlsx'
    chat_id = update.message.chat_id
    message_id = update.message.message_id

    login = context.user_data.get("login", "")
    password = context.user_data.get("password", "")

    # Send a preliminary message
    message = await update.message.reply_text(f"*SALES\.xlsx*\n\nfayl tayyorlanmoqda😎 \n\n"
                                              "||Iltimos kuting⌛⌛⌛\(Maksimum 8 daqiqa\)||", parse_mode='MarkdownV2',
                                              reply_to_message_id=message_id)

    try:
        if not os.path.exists(file_name):
            monthly_generator(login, password)

        modification_time = datetime.fromtimestamp(os.path.getmtime(file_name))
        current_time = datetime.now()
        time_difference = current_time - modification_time

        if time_difference >= timedelta(hours=2):
            monthly_generator(login, password)

        # Open and send the document
        with open(file_name, 'rb') as document:
            await context.bot.send_document(chat_id, document, caption=f"FEBRUARY SALES -> {today_date} 📈\n\n\n"
                                                                       f"🔁Updated: {modification_time.strftime('%d %B,%H:%M')}",
                                            reply_to_message_id=message_id)
        await message.delete()

        spoiler_text = ("|| Nixxuya charchatvordiz oka\!"
                        " Rosa qiynaldim formatlagani\, blin\! ||")
        await update.message.reply_text(spoiler_text, parse_mode='MarkdownV2')

    except Exception as e:
        # Handle exceptions and reply with an error message
        error_message = f'Error sending the file: {str(e)}'
        print(error_message)
        await update.message.reply_text(error_message, reply_to_message_id=message_id)


async def top_high_fav(update, context):
    message_id = update.message.message_id
    chat_id = update.message.chat_id

    current_date = datetime.now()
    formatted_date = f'{current_date.day} {current_date.strftime("%B")}'

    login = context.user_data.get("login", "")
    password = context.user_data.get("password", "")

    top_files = {
        'TOP_REVENUE_PRODUCTS_SOLD.xlsx': 'Товары, приносящие наибольший доход, среди клиентов в различных регионах и типах на',
        'HIGH_VOLUME_PRODUCTS.xlsx': 'Товары с наибольшим объемом(колич) продаж среди клиентов в различных регионах и типах на',
        'CLIENT_FAVORITE_PRODUCTS.xlsx': 'Товары, популярные среди клиентов в различных регионах и разных типов на'}
    message = await update.message.reply_text(
        f'Sizning so\'rovingiz bo\'yicha  \n *TOP REVENUE PRODUCTS SOLD\.xlsx* \n fayl tayyorlanmoqda😎 '
        'Iltimos kuting⌛⌛⌛ \(o\'rtacha 2 daqiqa\)', parse_mode='MarkdownV2', reply_to_message_id=message_id)

    try:
        for file, file_desc in top_files.items():
            top_product_sold_generator(login, password)
            # Open and send the document
            with open(file, 'rb') as document:
                caption_text = (f"\n\n{file_desc}\n<b><u>{formatted_date}</u></b>\n\n\n")

                main_file_message = await context.bot.send_document(chat_id, document, caption=caption_text,
                                                                    parse_mode='HTML', reply_to_message_id=message_id)

                for subtype in ['ROZ', 'Сеть']:
                    picture_file_path = f'reports/trash_media/Top_20_Goods_{file.split("_")[1]}_{subtype}.png'
                    with open(picture_file_path, 'rb') as picture:
                        if os.path.exists(picture_file_path):
                            await context.bot.send_photo(chat_id, photo=picture,
                                                         caption=f'ТОП 20 {file_desc} - {subtype}',
                                                         reply_to_message_id=main_file_message.message_id)

        await message.delete()
    except Exception as e:
        # Handle exceptions and reply with an error message
        error_message = f'Error sending the file: {str(e)}'
        print(error_message)
        await update.message.reply_text(error_message, reply_to_message_id=message_id)


async def delete_xlsx_files(update, context) -> None:
    # Get the chat ID and user ID for logging purposes
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id

    # Specify the directory where you want to delete '*.xlsx' files
    directory_path = './'

    try:
        # Iterate through files in the directory and try to delete '*.png' files with names longer than 11 characters
        for filename in os.listdir(directory_path):
            if filename.endswith(".xlsx"):
                file_path = os.path.join(directory_path, filename)
                try:
                    os.remove(file_path)
                    await update.message.reply_text(f'{filename} has been deleted successfully!')
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
    'LIMIT💸': limit,
    'OXVAT🙈': oxvat,
    'TOP OSTATOK🔄️': top, '🔝 TOP | FAV | HIGH SOLD': top_high_fav,
    'HOURLY⏳': hourly, '️Monthly  ⛏️️️': monthly,  # 'FINSKIDKA📈': to_finskidka,
    'Jokes about Gulya😅': gulya_jokes, '🤠 Chuck Norris Jokes 😁': chuck_norris_jokes,
    '🗑️ Clear Files': delete_xlsx_files, '🖼️ Delete PNG': delete_png_files}
