import telebot
import requests
import datetime
from telebot import types
from constant import telegram_token, weather_token

bot = telebot.TeleBot(telegram_token)


@bot.message_handler(commands=['start'])
def handle_start(message):
    """Adding buttons to reply"""
    markup = types.ReplyKeyboardMarkup(row_width=2)
    button_city = types.KeyboardButton('Select City')
    button_forecast = types.KeyboardButton('2-day Forecast')
    button_end = types.KeyboardButton('End')
    markup.add(button_city, button_forecast, button_end)
    bot.reply_to(message, "Welcome to Weather Bot!", reply_markup=markup)
    bot.reply_to(message, "If you need help print '/help'. ", reply_markup=markup)


@bot.message_handler(commands=['help'])
def handle_help(message):
    """Help message for user"""
    bot.reply_to(message, "Usage: /weather <city>")


@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    """Answers given to responses using buttons"""
    if message.text == 'Select City':
        bot.reply_to(message, "Please enter the city name.")
        bot.register_next_step_handler(message, handle_weather)
    elif message.text == '2-day Forecast':
        bot.reply_to(message, "Please enter the city name for the 10-day forecast.")
        bot.register_next_step_handler(message, handle_forecast)
    elif message.text == 'End':
        bot.reply_to(message, "Thank you for using Weather Bot! Goodbye.")
    else:
        bot.reply_to(message, "Please select a valid option.")


@bot.message_handler(commands=['weather'])
def handle_weather(message):
    """Main function. Parameters, smiles, data to show to the user"""
    code_to_smile = {
        "Clear": "Clear \U00002600",
        "Clouds": "Clouds \U00002601",
        "Rain": "Rain \U00002614",
        "Drizzle": "Rain \U00002614",
        "Thunderstorm": "Thunderstorm \U000026A1",
        "Snow": "Snow \U0001F328",
        "Mist": "Mist \U0001F328"
    }
    try:
        city = message.text
        url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_token}&units=metric'
        response = requests.get(url)
        data = response.json()

        if response.status_code != 200:
            bot.reply_to(message, "Could not retrieve weather data. Please check the city name.")
            return

        city = data["name"]
        cur_weather = data["main"]["temp"]
        weather_description = data["weather"][0]["main"]
        if weather_description in code_to_smile:
            wd = code_to_smile[weather_description]
        else:
            wd = "Look in the window"

        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind = data["wind"]["speed"]
        sunrise_time = datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
        sunset_time = datetime.datetime.fromtimestamp(data["sys"]["sunset"])
        length_of_the_day = datetime.datetime.fromtimestamp(data["sys"]["sunset"]) - datetime.datetime.fromtimestamp(
            data["sys"]["sunrise"])

        weather_message = (f"***{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}***\n"
                           f"Weather in the city: {city}\nTemperature: {cur_weather} C° {wd}\n"
                           f"Humidity: {humidity} %\nPressure: {pressure} mm Hg\n"
                           f"Wind: {wind} m/s\nSunrise time: {sunrise_time}\n"
                           f"Sunset: {sunset_time}\nLength of the day: {length_of_the_day}")
        bot.reply_to(message, weather_message)

    except IndexError:
        bot.reply_to(message, "Please specify a city after /weather command.")
    except Exception as e:
        bot.reply_to(message, f"An error occurred: {e}")


def handle_forecast(message):
    """Handle 2-day weather forecast"""

    try:
        city = message.text
        url = f'https://api.openweathermap.org/data/2.5/forecast?q={city}&cnt=10&appid={weather_token}&units=metric'
        response = requests.get(url)
        data = response.json()

        if response.status_code != 200:
            bot.reply_to(message, "Could not retrieve 2-day forecast data. Please check the city name.")
            return

        daily_temps = {}
        for forecast in data['list']:
            date = datetime.datetime.fromtimestamp(forecast['dt']).strftime('%Y-%m-%d')
            temp = forecast['main']['temp']

            if date in daily_temps:
                daily_temps[date].append(temp)
            else:
                daily_temps[date] = [temp]

        forecast_message = f"***2-Day Forecast for {city}***\n\n"
        for date, temps in daily_temps.items():
            avg_temp = sum(temps) / len(temps)
            weather_description = data['list'][0]['weather'][0]['description']

            forecast_message += (f"{date}\n"
                                 f"Avg Temperature: {avg_temp:.2f}°C\n"
                                 f"Weather: {weather_description}\n\n")

        bot.reply_to(message, forecast_message)

    except Exception as e:
        bot.reply_to(message, f"An error occurred: {e}")


bot.polling()
