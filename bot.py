
# coding: utf-8

# In[1]:
from pymongo import MongoClient
import pymongo
import datetime
import time
import telebot
from telebot import types

template_popular = "Самыми популярными словами на сегодня были: \n"
template_mood = "Общее настроение авторов: \n"
template_cash = "Самые денежные слова на сегодня: \n"
template_votes = "Слова, вызывающие наибольшее количество апвойтов: \n"
template_comms = "Слова с наибольшим общественным резонансом: \n"

db = MongoClient().golos

# In[5]:

#markup = types.ReplyKeyboardMarkup()
#markup.row('/stats')
token = "token_bot"
bot = telebot.TeleBot(token)
url = "https://api.telegram.org/bot%s/", token

@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text="Today", callback_data=str(message.chat.id) + "_data")
    keyboard.add(btn)
    btn1= types.InlineKeyboardButton(text="Choose date(WIP)", callback_data=str(message.chat.id) +"_date")
    keyboard.add(btn1)
    bot.send_message(message.chat.id, "Привет, хочешь узнать статитстику по платформе голос? Выбирай дату:",reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    s = call.data.split("_")
    if s[1] == "date":
        bot.send_message(s[0],s[1])
    else:
        bot.send_message(s[0],"Выберите дату:")

def main():
    signal.signal(signal.SIGINT, signal_handler)
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as err:
            time.sleep(30)

def signal_handler(signal_number, frame):
    print('Received signal ' + str(signal_number)
          + '. Trying to end tasks and exit...')
    bot.stop_polling()
    sys.exit(0)

if __name__ == "__main__":
    main()

