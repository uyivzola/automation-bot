# buttons.py
import os
from datetime import datetime

import requests

from reports.hourly import hourly_generator
from reports.limit import limit_generator
from reports.montly import monthly_generator
from reports.oxvat import oxvat_generator
from reports.top import top_generator


async def facts_about_cats(update, context):
    req = requests.get("https://cat-fact.herokuapp.com/facts/random?animal_type=cat&amount=5", verify=False)

    if req.status_code == 200:
        # Parse the JSON response
        response_json = req.json()

        # Extract the "text" values from each item in the response
        texts = [item["text"] for item in response_json]

        # Print the extracted text values
        for text in texts:
            print(text)
            await update.message.reply_text(f"{text}")
    else:
        # Print an error message if the request was not successful
        print(f"Error: {req.status_code}")
        await update.message.reply_text(f"{req.status_code}")


async def oxvat(update, context):
    user = update.message.from_user
    username = user.first_name

    today_date = datetime.now().strftime('%d %b')
    file_name = f'NE OXVACHEN - {today_date}.xlsx'
    chat_id = update.message.chat_id
    # Send a preliminary message
    message = await update.message.reply_text(f'*NE OXVACHEN \- {today_date}\.xlsx*\n\nfayl tayyorlanmoqda😎\n\n'
                                              '||Iltimos kuting⌛⌛⌛\(Maksimum 3 daqiqa\)||', parse_mode='MarkdownV2')
    try:
        oxvat_generator()
        # Check the modification time of the file
        modification_time = datetime.fromtimestamp(os.path.getmtime(file_name))

        # Open and send the document
        document = open(file_name, 'rb')
        await context.bot.send_document(chat_id, document, caption=f"Mijozlar bilan xushmomila bo'ling🙈\n \n\n"
                                                                   f"🔁Updated: {modification_time.strftime('%d %B, %H:%M')} ⌚")

        # Delete the preliminary message
        await message.delete()

    except Exception as e:
        # Handle exceptions and reply with an error message
        error_message = f'Error sending the file: {str(e)}'
        print(error_message)
        await update.message.reply_text(error_message)


async def top(update, context):
    user = update.message.from_user
    username = user.first_name

    today_date = datetime.now().strftime('%d %b')
    file_name = f'TOP ostatok - {today_date}.xlsx'
    chat_id = update.message.chat_id

    # Send a preliminary message
    message = await update.message.reply_text(
        f"Sizning so\'rovingiz bo\'yicha \n *TOP ostatok \- {today_date}\.xlsx* \nfayl tayyorlanmoqda😎 "
        "Iltimos kuting⌛\(Maksimum 3 daqiqa\)", parse_mode='MarkdownV2')
    try:

        top_generator()
        # Check the modification time of the file
        modification_time = datetime.fromtimestamp(os.path.getmtime(file_name))

        # Open and send the document
        document = open(file_name, 'rb')
        await context.bot.send_document(chat_id, document,
                                        caption=f"Asklepiy Distribution Skladidagi Tovarlar ro'yxati📑. \n\n"
                                                f"Ishizga omad, {username}!😉\n\n\n"
                                                f"🔁Updated: {modification_time.strftime('%d %B,%H:%M')}")
        # Delete the preliminary message
        await message.delete()

    except Exception as e:
        # Handle exceptions and reply with an error message
        error_message = f'Error sending the file: {str(e)}'
        print(error_message)
        await update.message.reply_text(error_message)


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
                                        caption=f"Savdoyingizga baraka bersin!🤲🏼💸, Hurmatli {username}!😻\n \n\n"
                                                f"🔁Updated: {modification_time.strftime('%d %B,%H:%M')}")

        # Delete the preliminary message
        await message.delete()

    except Exception as e:
        # Handle exceptions and reply with an error message
        error_message = f'Error sending the file: {str(e)}'
        print(error_message)
        await update.message.reply_text(error_message)


async def hourly(update, context):
    user = update.message.from_user
    username = user.first_name

    today_date = datetime.now().strftime('%d %b')
    file_name = f'HOURLY.xlsx'
    chat_id = update.message.chat_id

    # Send a preliminary message
    message = await update.message.reply_text(f"*HOURLY \- {today_date}\.xlsx* \n fayl tayyorlanmoqda😎 \n\n"
                                              "||Iltimos kuting⌛⌛⌛\(Maksimum 3 daqiqa\)||", parse_mode='MarkdownV2')

    try:
        hourly_generator()
        # Check the modification time of the file
        modification_time = datetime.fromtimestamp(os.path.getmtime(file_name))

        # Open and send the document
        document = open(file_name, 'rb')
        await context.bot.send_document(chat_id, document,
                                        caption=f"Analitikangizga aniqlik tilayman!📈, {username}💋💖!\n \n\n"
                                                f"🔁Updated: {modification_time.strftime('%d %B,%H:%M')}")

        # Delete the preliminary message
        await message.delete()  # Send a final message

    except Exception as e:
        # Handle exceptions and reply with an error message
        error_message = f'Error sending the file: {str(e)}'
        print(error_message)
        await update.message.reply_text(error_message)


async def monthly(update, context):
    today_date = datetime.now().strftime('%d %b')
    file_name = f'MONTHLY.xlsx'
    chat_id = update.message.chat_id

    # Send a preliminary message
    message = await update.message.reply_text(f"*SALES\.xlsx*\n\nfayl tayyorlanmoqda😎 \n\n"
                                              "||Iltimos kuting⌛⌛⌛\(Maksimum 8 daqiqa\)||", parse_mode='MarkdownV2')

    try:
        monthly_generator()
        # Check the modification time of the file
        modification_time = datetime.fromtimestamp(os.path.getmtime(file_name))

        # Open and send the document
        document = open(file_name, 'rb')
        await context.bot.send_document(chat_id, document, caption=f"JANUARY SALES -> {today_date} 📈\n\n\n"
                                                                   f"🔁Updated: {modification_time.strftime('%d %B,%H:%M')}")
        await message.delete()

        spoiler_text = ("|| Nixxuya charchatvordiz oka\!"
                        " Rosa qiynaldim formatlagani\, blin\! ||")
        await update.message.reply_text(spoiler_text, parse_mode='MarkdownV2')

    except Exception as e:
        # Handle exceptions and reply with an error message
        error_message = f'Error sending the file: {str(e)}'
        print(error_message)
        await update.message.reply_text(error_message)


button_functions = {'LIMIT💸': limit, 'OXVAT🙈': oxvat, 'TOP🔄️': top, 'HOURLY⏳': hourly, '️Monthly  ⛏️️️': monthly,
                    'Facts about cats🐈': facts_about_cats}
