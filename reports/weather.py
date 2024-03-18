import matplotlib.pyplot as plt
import pandas as pd
import requests
import seaborn as sns


async def weather(update, context):
    # Fetch data from the API
    url = 'https://api.open-meteo.com/v1/forecast?latitude=41.2647&longitude=69.2163&hourly=temperature_2m&forecast_days=1'
    response = requests.get(url).json()
    picture = 'weather.png'

    # Extract hourly timestamps and temperatures
    hourly_data = response['hourly']
    timestamps = hourly_data['time']
    temperatures = hourly_data['temperature_2m']

    # Create a DataFrame
    df = pd.DataFrame({'Timestamp': timestamps, 'Temperature (°C)': temperatures})

    # Parse hours from timestamps for x-axis
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['Hour'] = df['Timestamp'].dt.hour

    # Function to format dates with ordinal suffixes
    def format_date_with_suffix(date):
        day = date.day
        if 4 <= day <= 20 or 24 <= day <= 30:
            suffix = "th"
        else:
            suffix = ["st", "nd", "rd"][day % 10 - 1]
        return date.strftime("%B %d") + suffix

    # Generate caption message
    caption = "Weather for today:\n\n"
    for index, row in df.iterrows():
        formatted_date = format_date_with_suffix(row['Timestamp'])
        # time_suffix = 'midnight' if row['Timestamp'].hour < 12 else 'noon'
        temperature = row['Temperature (°C)']
        emoji = '☀️' if temperature >= 25 else '⛅️' if temperature >= 15 else '☁️' if temperature >= 5 else '❄️'

        caption += f"{formatted_date} at {row['Hour']}:00: {temperature:.1f}°C {emoji}\n"
    # Plot using Seaborn
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df, x='Hour', y='Temperature (°C)', markersize=8, color='darkmagenta', marker='2')

    # Annotate every 12th point with temperature value
    for index, row in df.iterrows():
        if index % 4 == 0:  # Only annotate every 12th point
            formatted_date = format_date_with_suffix(row['Timestamp'])
            time_suffix = 'am' if row['Timestamp'].hour < 12 else 'pm'
            temperature = row['Temperature (°C)']
            emoji = '☀️' if temperature >= 25 else '⛅️' if temperature >= 15 else '☁️' if temperature >= 5 else '❄️'

            plt.text(row['Hour'], temperature, f"{formatted_date}\nat {row['Hour']}:00\n{temperature:.1f}°C",
                     horizontalalignment='left', fontsize=10, color='navy', weight='bold')

    plt.title('Hourly Temperature in Tashkent', fontsize=18)
    plt.xlabel('Hour of the Day')
    plt.ylabel('Temperature (°C)')
    plt.savefig(picture)

    # Send photo with caption
    user = update.message.from_user
    message_id = update.message.message_id
    chat_id = update.message.chat_id

    with open(picture, 'rb') as picture:
        await context.bot.send_photo(chat_id, photo=picture, caption=caption, reply_to_message_id=message_id)

    # Close plot to avoid memory leaks
    plt.close()
