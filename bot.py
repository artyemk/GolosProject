
# coding: utf-8


# In[1]:
from datetime import datetime
from pymongo import MongoClient
import pymongo
import sys
from datetime import datetime
import time
import telebot
import signal
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
token = "541950328:AAH1idc0uCTFDKH3oXsUlxk_Qvq0EiZcQGY"
bot = telebot.TeleBot(token)
url = "https://api.telegram.org/bot%s/", token

@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text="Today", callback_data=str(message.chat.id) + "_today")
    keyboard.add(btn)
    btn1= types.InlineKeyboardButton(text="Choose date(WIP)", callback_data=str(message.chat.id) +"_date")
    keyboard.add(btn1)
    bot.send_message(message.chat.id, "Привет, хочешь узнать статитстику по платформе голос? Выбирай дату:",reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    keybd = types.InlineKeyboardMarkup()
    s = call.data.split("_")
    if s[1] == "today":
        stats = db.stots.find_one({"date": str(datetime.now()).split(" ")[0]}) 
        user_text(s[0],stats['popular'],stats['mood'],stats['stats'])
    elif s[1] == "date":
        for i in db.stots.distinct("date"):
            keybd.add(types.InlineKeyboardButton(text=i, callback_data=s[0] + "_" + i))
        bot.send_message(s[0],"Выберите дату📅",reply_markup=keybd)
    else:
        stats = db.stots.find_one({"date": s[1]})
        user_text(s[0],stats['popular'],stats['mood'],stats['stats'])

def user_text(message,popular,mood,stats):
    res_popular = ""
    arr = []
    res_cash = ""
    res_votes = ""
    res_comms = ""
    sort_cash = []
    sort_votes = []
    sort_comms = []
    count = 1
    for item in popular:
        res_popular += str(count) + ") " + str(item[0]) + ": " + str(item[1]) + "\n"
        count += 1
        if count == 10:
            count = 0
            break
    for item in stats:
        temp1 = [item['word'], round(item['avg_cash'],2)]
        temp2 = [item['word'], round(item['avg_votes'],2)]
        temp3 = [item['word'], round(item['avg_comms'],2)]
        sort_cash.append(temp1)
        sort_votes.append(temp2)
        sort_comms.append(temp3)
    sort_cash.sort(reverse = True, key=lambda x: x[1])
    sort_votes.sort(reverse = True, key=lambda x: x[1])
    sort_comms.sort(reverse = True, key=lambda x: x[1])
    for item in sort_cash:
        count += 1
        res_cash += str(count) + ")" + str(item[0]) + ": " + str(item[1]) + "\n"
        if count == 10:
            count = 0
            break
    for item in sort_votes:
        count += 1
        res_votes += str(count) + ")" + str(item[0]) + ": " + str(item[1]) + "\n"
        if count == 10:
            count = 0
            break
    for item in sort_comms:
        count += 1
        res_comms += str(count) + ")" + str(item[0]) + ": " + str(item[1]) + "\n"
        if count == 10:
            count == 0
            break
    bot.send_message(message, "Статистика собрана:")
    bot.send_message(message, template_popular + res_popular)
    bot.send_message(message, template_mood +
                         "Позитивных постов: " +str(mood["positive_posts"]) + "\n" +
                         "Негативных постов: " + str(mood["negative_posts"]) + "\n" +
                         "Нейтральных постов: " + str(mood["neutral_posts"]) + "\n")
    bot.send_message(message, template_cash + res_cash)
    bot.send_message(message, template_votes + res_votes)
    bot.send_message(message, template_comms + res_comms)

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

