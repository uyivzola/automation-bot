# buttons.py
import os
import random
from datetime import datetime

import requests

from reports.gulya_jokes import gulya_opa_jokes
from reports.hourly import hourly_generator
from reports.limit import limit_generator
from reports.montly import monthly_generator
from reports.oxvat import oxvat_generator
from reports.to_finskidka import to_finskidka_generator
from reports.top import top_generator


async def chuck_norris_jokes(update, context):
    message_id = update.message.message_id
    message_text = update.message.text
    message = await update.message.reply_text(f"i am thinking about the joke about {message_text}",
                                              reply_to_message_id=message_id)

    req = requests.get("https://api.chucknorris.io/jokes/random", verify=False)

    if req.status_code == 200:
        # Parse the JSON response
        response_json = req.json()

        text = response_json["value"]
        # Print the extracted text VALUE
        print(text)
        await message.edit_text(text)  # await update.message.delete()

    else:
        # Print an error message if the request was not successful
        await message.delete()
        print(f"Error: {req.status_code}")
        await update.message.reply_text(f"{req.status_code}", reply_to_message_id=message_id)


async def gulya_jokes(update, context):
    message_id = update.message.message_id
    message_text = update.message.text
    message = await update.message.reply_text(f"i am thinking about the joke about {message_text}",
                                              reply_to_message_id=message_id)

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


async def oxvat(update, context):
    chat_id = update.message.chat_id
    message_id = update.message.message_id

    today_date = datetime.now().strftime('%d %b')
    file_name = f'NE OXVACHEN - {today_date}.xlsx'

    # Send a preliminary message
    message = await update.message.reply_text(f'*NE OXVACHEN \- {today_date}\.xlsx*\n\nfayl tayyorlanmoqda😎\n\n'
                                              '||Iltimos kuting⌛⌛⌛\(Maksimum 3 daqiqa\)||', parse_mode='MarkdownV2',
                                              reply_to_message_id=message_id)
    try:
        oxvat_generator()
        # Check the modification time of the file
        modification_time = datetime.fromtimestamp(os.path.getmtime(file_name))

        # Open and send the document
        document = open(file_name, 'rb')
        await context.bot.send_document(chat_id, document,
                                        caption=f"\n\n\n🔁Updated: {modification_time.strftime('%d %B, %H:%M')} ⌚",
                                        reply_to_message_id=message_id)

        # Delete the preliminary message
        await message.delete()

    except Exception as e:
        # Handle exceptions and reply with an error message
        error_message = f'Error sending the file: {str(e)}'
        print(error_message)
        await update.message.reply_text(error_message, reply_to_message_id=message_id)


async def top(update, context):
    user = update.message.from_user
    chat_id = update.message.chat_id
    message_id = update.message.message_id

    today_date = datetime.now().strftime('%d %b')
    file_name = f'TOP ostatok - {today_date}.xlsx'
    # Send a preliminary message
    message = await update.message.reply_text(
        f"Sizning so\'rovingiz bo\'yicha \n *TOP ostatok \- {today_date}\.xlsx* \nfayl tayyorlanmoqda😎 "
        "Iltimos kuting⌛\(Maksimum 3 daqiqa\)", parse_mode='MarkdownV2', reply_to_message_id=message_id)
    try:

        top_generator()
        # Check the modification time of the file
        modification_time = datetime.fromtimestamp(os.path.getmtime(file_name))

        # Open and send the document
        document = open(file_name, 'rb')
        await context.bot.send_document(chat_id, document, caption=f"\n\n\n\n\n"
                                                                   f"🔁Updated: {modification_time.strftime('%d %B,%H:%M')}",
                                        reply_to_message_id=message_id)

        # Delete the preliminary message
        await message.delete()

    except Exception as e:
        # Handle exceptions and reply with an error message
        error_message = f'Error sending the file: {str(e)}'
        print(error_message)
        await update.message.reply_text(error_message, reply_to_message_id=message_id)


async def limit(update, context):
    user = update.message.from_user
    message_id = update.message.message_id

    today_date = datetime.now().strftime('%d %b')
    file_name = f'LIMIT - {today_date}.xlsx'
    chat_id = update.message.chat_id

    # Send a preliminary message
    message = await update.message.reply_text(
        f"Sizning so\'rovingiz bo\'yicha  \n *LIMIT \- {today_date}\.xlsx* \n fayl tayyorlanmoqda😎 "
        "Iltimos kuting⌛⌛⌛ \(o\'rtacha 5 daqiqa\)", parse_mode='MarkdownV2', reply_to_message_id=message_id)

    try:

        limit_generator()
        # Check the modification time of the file
        modification_time = datetime.fromtimestamp(os.path.getmtime(file_name))

        # Open and send the document
        document = open(file_name, 'rb')
        await context.bot.send_document(chat_id, document, caption=f"\n\n\n\n\n"
                                                                   f"🔁Updated: {modification_time.strftime('%d %B,%H:%M')}",
                                        reply_to_message_id=message_id)

        # Delete the preliminary message
        await message.delete()

    except Exception as e:
        # Handle exceptions and reply with an error message
        error_message = f'Error sending the file: {str(e)}'
        print(error_message)
        await update.message.reply_text(error_message, reply_to_message_id=message_id)


async def hourly(update, context):
    user = update.message.from_user
    first_name = user.first_name
    message_id = update.message.message_id

    today_date = datetime.now().strftime('%d %b')
    file_name = f'HOURLY.xlsx'
    chat_id = update.message.chat_id

    # Send a preliminary message
    message = await update.message.reply_text(f"*HOURLY \- {today_date}\.xlsx* \n fayl tayyorlanmoqda😎 \n\n"
                                              "||Iltimos kuting⌛⌛⌛\(Maksimum 3 daqiqa\)||", parse_mode='MarkdownV2',
                                              reply_to_message_id=message_id)

    try:
        hourly_generator()
        # Check the modification time of the file
        modification_time = datetime.fromtimestamp(os.path.getmtime(file_name))

        # Open and send the document
        document = open(file_name, 'rb')
        await context.bot.send_document(chat_id, document,
                                        caption=f"Analitikangizga aniqlik tilayman!📈, {first_name}💋💖!\n \n\n"
                                                f"🔁Updated: {modification_time.strftime('%d %B,%H:%M')}",
                                        reply_to_message_id=message_id)

        # Delete the preliminary message
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

    today_date = datetime.now().strftime('%d %b')
    file_name = f'TOandFinSkidka.xlsx'
    chat_id = update.message.chat_id

    # Send a preliminary message
    message = await update.message.reply_text(f"*TOandFinSkidka \- {today_date}\.xlsx* \n fayl tayyorlanmoqda😎 \n\n"
                                              "||Iltimos kuting⌛⌛⌛\(Maksimum 3 daqiqa\)||", parse_mode='MarkdownV2',
                                              reply_to_message_id=message_id)

    try:
        to_finskidka_generator()
        # Check the modification time of the file
        modification_time = datetime.fromtimestamp(os.path.getmtime(file_name))

        # Open and send the document
        document = open(file_name, 'rb')
        await context.bot.send_document(chat_id, document,
                                        caption=f"Analitikangizga aniqlik tilayman!📈, {username}!\n \n\n"
                                                f"🔁Updated: {modification_time.strftime('%d %B,%H:%M')}",
                                        reply_to_message_id=message_id)

        # Delete the preliminary message
        await message.delete()  # Send a final message

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

    # Send a preliminary message
    message = await update.message.reply_text(f"*SALES\.xlsx*\n\nfayl tayyorlanmoqda😎 \n\n"
                                              "||Iltimos kuting⌛⌛⌛\(Maksimum 8 daqiqa\)||", parse_mode='MarkdownV2',
                                              reply_to_message_id=message_id)

    try:
        monthly_generator()
        # Check the modification time of the file
        modification_time = datetime.fromtimestamp(os.path.getmtime(file_name))

        # Open and send the document
        document = open(file_name, 'rb')
        await context.bot.send_document(chat_id, document, caption=f"JANUARY SALES -> {today_date} 📈\n\n\n"
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


button_functions = {'LIMIT💸': limit, 'OXVAT🙈': oxvat, 'TOP🔄️': top, 'HOURLY⏳': hourly, '️Monthly  ⛏️️️': monthly,
                    'FINSKIDKA📈': to_finskidka, 'Jokes about Gulya😅': gulya_jokes,
                    '🤠 Chuck Norris Jokes 😁': chuck_norris_jokes, }
