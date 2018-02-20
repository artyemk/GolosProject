
# coding: utf-8

# In[1]:


import os
import subprocess
import threading
import get_stat
import sys
import signal
import re
import time
from logging import log
import telebot


template_popular = "Самыми популярными словами на сегодня были: \n"
template_mood = "Общее настроение авторов: \n"
template_cash = "Самые денежные слова на сегодня: \n"
template_votes = "Слова, вызывающие наибольшее количество апвойтов: \n"
template_comms = "Слова с наибольшим общественным резонансом: \n"


# In[5]:


token = "543294251:AAF-IpOvlt9aV1TgPbg212Lw_Le2244hCw8"
bot = telebot.TeleBot(token)
url = "https://api.telegram.org/bot%s/", token

var = get_stat.get_article_info('2018-02-20')

print("check")
popular = get_stat.norm_text()
print("Popular parsed")
print(popular)
mood = get_stat.comment_analysis()
print("Mood parsed")
print(mood)

stats = get_stat.hoy(popular, var)
print("Stats parsed")
print(stats)
print("Bot ready")

@bot.message_handler(commands=['stats'])
def get_stats_msg(message):
    bot.send_message(message.chat.id, "Анализирую собранную статистику. Пожалуйста подождите...")

    res_popular = ""
    for item in popular:
        res_popular += str(item[0]) + ": " + str(item[1]) + "\n"
    print(res_popular)
    res_cash = ""
    res_votes = ""
    res_comms = ""

    for item in stats:
        res_cash += str(item["word"]) + ": " + str(item["avg_cash"]) + "\n"
        res_votes += str(item["word"]) + ": " + str(item["avg_votes"]) + "\n"
        res_comms += str(item["word"]) + ": " + str(item["avg_comms"]) + "\n"
    print(res_cash)
    print(res_votes)
    print(res_comms)
    bot.send_message(message.chat.id, "Статистика собрана:")
    time.sleep(3)
    bot.send_message(message.chat.id, template_popular + res_popular)
    bot.send_message(message.chat.id, template_mood +
                         "Позитивных постов: " +str(mood["positive_comments"]) + "\n" +
                         "Негативных постов: " + str(mood["negative_comments"]) + "\n" +
                         "Нейтральных постов: " + str(mood["neutral_comments"]) + "\n")
    bot.send_message(message.chat.id, template_cash + res_cash)
    time.sleep(2)
    bot.send_message(message.chat.id, template_votes + res_votes)
    time.sleep(1)
    bot.send_message(message.chat.id, template_comms + res_comms)


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

