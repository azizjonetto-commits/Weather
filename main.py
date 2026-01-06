import telebot
from telebot import types
import requests
from datetime import datetime, timedelta

API_KEY_BOT = "8314505865:AAEYW7L2ZT4BOxRkCMF15opu-FI3XahW6vk"
API_KEY_WEATHER = "9bfe4c7ba5f9832babe15ed33d4fb047"

bot = telebot.TeleBot(API_KEY_BOT)

user_city = {}

cities = {
    "toshkent": "Tashkent",
    "samarqand": "Samarkand",
    "buxoro": "Bukhara",
    "namangan": "Namangan",
    "andijon": "Andijan",
    "qarshi": "Karshi",
    "shahrisabz": "Shahrisabz",
    "nukus": "Nukus",
    "fergana": "Fergana",
    "jizzax": "Jizzakh",
    "navoiy": "Navoi",
    "termez": "Termez",
    "urganch": "Urgench",
}

weather_desc_uz = {
    "clear sky": "Toza havo ☀",
    "few clouds": "Kam bulutli 🌤",
    "scattered clouds": "Tarqalgan bulutlar ☁",
    "broken clouds": "Bulutli ☁",
    "shower rain": "Yomg‘irli 🌧",
    "rain": "Yomg‘ir 🌦",
    "thunderstorm": "Momaqaldiroq ⛈",
    "snow": "Qor ❄",
    "mist": "Tuman 🌫",
}

def city_buttons():
    markup = types.InlineKeyboardMarkup(row_width=2)
    for uz in cities:
        markup.add(
            types.InlineKeyboardButton(
                uz.title(), callback_data=f"city_{uz}"
            )
        )
    return markup

def weather_buttons():
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Bugungi 🌤", callback_data="today"),
        types.InlineKeyboardButton("Ertangi ⛅", callback_data="tomorrow"),
    )
    return markup

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Salom! 👋\nMen ob-havo botiman. Sizga O'zbekiston hududidagi shaharlarning bugungi va ertangi ob-havo ma’lumotlarini beraman.")
    bot.send_message(
        message.chat.id,
        "\n\nShaharni tanlang:",
        reply_markup=city_buttons()
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("city_"))
def choose_city(call):
    city_uz = call.data.replace("city_", "")
    user_city[call.message.chat.id] = cities[city_uz]

    bot.edit_message_text(
        f"📍 {city_uz.title()} shahri tanlandi.\n\nQaysi kunni tanlaysiz?",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=weather_buttons()
    )

@bot.callback_query_handler(func=lambda call: call.data in ["today", "tomorrow"])
def weather_info(call):
    chat_id = call.message.chat.id
    city = user_city.get(chat_id)

    if not city:
        bot.answer_callback_query(call.id, "Avval shaharni tanlang")
        return

    if call.data == "today":
        target_day = datetime.now().date()
        day_text = "Bugungi"
    else:
        target_day = (datetime.now() + timedelta(days=1)).date()
        day_text = "Ertangi"

    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY_WEATHER}&units=metric&lang=en"
    res = requests.get(url).json()

    if res.get("cod") != "200":
        bot.send_message(chat_id, "Maʼlumot topilmadi 😕")
        return

    forecasts = [
        f for f in res["list"]
        if datetime.strptime(f["dt_txt"], "%Y-%m-%d %H:%M:%S").date() == target_day
    ]

    avg_temp = sum(f["main"]["temp"] for f in forecasts) / len(forecasts)
    avg_humidity = sum(f["main"]["humidity"] for f in forecasts) / len(forecasts)
    avg_wind = sum(f["wind"]["speed"] for f in forecasts) / len(forecasts)

    desc_en = forecasts[0]["weather"][0]["description"]
    desc_uz = weather_desc_uz.get(desc_en.lower(), desc_en)

    text = (
        f"🌆 {city}\n"
        f"📅 {day_text} ob-havo\n"
        f"🌡 Harorat: {avg_temp:.1f}°C\n"
        f"💧 Namlik: {avg_humidity:.0f}%\n"
        f"💨 Shamol: {avg_wind:.1f} m/s\n"
        f"☁ Havo: {desc_uz}"
    )

    bot.send_message(chat_id, text)

print("Bot ishga tushdi")
bot.infinity_polling()
