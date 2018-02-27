#-*- coding: utf-8 -*-
#from __future__ import unicode_literals
from websocket import WebSocket
from pymongo import MongoClient
import sent
import re
from nltk.corpus import stopwords
from pymorphy2 import MorphAnalyzer
from collections import Counter
import json
import schedule
from time import sleep
from datetime import datetime, timedelta

#connecting to golos and db
ws = WebSocket()
ws.connect('wss://api.golos.cf')
db = MongoClient().golos

#preventing misrecognition of variables in input
true = True
false = False
null = None


#scheduled basic analysis func
def analyze(timestamp):
    #setting up base variables
    analysis = {}
    text = ''
    posts_array = []
    pos = 0
    neg = 0
    neu = 0
    total_dump=[]
    print('Going for it')
#parsing db for data and golos for post params
    for i in db.posts.find({'timestamp':timestamp}):
        ws.send(json.dumps({"id":1,"method":"get_content","params":[i['author'],i['permlink']]}))
        info = eval(ws.recv())['result']
#         ws.send(json.dumps({"id":3,"method":"get_content_replies","params":[i['author'],i['permlink']]}))
#         comm = []
#         for j in eval(ws.recv())['result'][0]:
#             comm.append(j['body'])
#             print('commy_found')
        try:
            tags = eval(info['json_metadata'])['tags']
        except:
            tags = ''
        dump = {'id':info['id'],'body':info['body'], 'tags':tags,
                'reward': float(info['pending_payout_value'].split()[0]),
                'comments': info['children'], 'votes':info['net_votes']}
        total_dump.append(dump)
        
    print('Starting analysis session')
    for i in total_dump:
        posts_array.append(i['body'])
        text += i['body'] + ' '
    print('Starting the mood')

#neurolinguistic analysis on post altitude
    for post in posts_array:
        if sent.foo(post) == 'Positive':
            pos +=1
        elif sent.foo(post) == 'Negative':
            neg +=1
        elif sent.foo(post) == 'Neutral':
            neu +=1
#normalizing raw_text
    print('Normalization')
    text_norm = []
    cnt = Counter()
    r = re.sub(r"<.*?>",' ',str(text))
    r1 = re.sub(r"(\\+\w+)",' ',str(r))
    r2 = re.sub(r"(&nbsp)",' ',str(r1))
    r3 = re.sub(r"(%\w+)",' ',str(r2))
    r4 = re.sub(r"(\.)",' ',str(r3))
    r5 = re.sub(r"(\?)",' ',str(r4))
    r6 = re.sub(r"(,)",' ',str(r5))
    r7 = re.sub(r"(\\n)",' ',str(r6)) 
    r8 = re.sub(r"(https://\w+.\w+.\w+/\w+/\w+.\w+)",' ',str(r7))
    r9 = re.sub(r"(\))",' ',str(r8))
    r10 = re.sub(r"(\()",' ',str(r9))
    r11 = re.sub(r"(!)",' ',str(r10))
    r12 = re.sub(r"(])",' ',str(r11))
    r13 = re.sub(r"(\[)",' ',str(r12))
    r14 = re.sub(r"(;)",' ',str(r13))
    r15 = re.sub(r"(-)",' ',str(r14))
    r16 = re.sub(r"(:)",' ',str(r15))
    morph = MorphAnalyzer().parse
    for word in r16.split():
        p = morph(word)[0]
        if p.tag.POS == 'NOUN':
            text_norm.append(p.normal_form)
        else:
            pass
    print('Finding Popular')
#getting most used words
    popular=()
    for word in text_norm:
        if word not in stopwords.words('russian'):
            if len(word)>2:
                cnt[word] += 1
                popular = cnt.most_common(100)

    mood = {"positive_posts":pos,
            "negative_posts": neg,
            "neutral_posts": neu}
    print('Final countdown')
    
    total = []
    
#getting avg stats
    for word in popular:
        count = 0
        gbg = 0
        votes = 0
        comms = 0
        temp = {}
        for post in total_dump:
            if word[0] in post['body']:
                count += 1
                gbg += post['reward']
                votes += post['votes']
                comms += post['comments']
        temp['word'] = word[0]
        try:
            temp['avg_cash'] = gbg/count
        except:
            temp['avg_cash'] = 0
        try:
            temp['avg_votes'] = votes/count
        except:
            temp['avg_votes'] = 0
        try:
            temp['avg_comms'] = comms/count
        except:
            temp['avg_comms'] = 0
        total.append(temp)
    
#inserting in DB
    analysis = {'date': timestamp,
               'popular': popular,
               'mood': mood,
               'stats': total}
    print(str(analysis).encode('utf-8'))
    return db.stots.insert_one(analysis)

#getting current timestamp to golos format
def get_str_date():
    date = datetime.now() - timedelta(days=1)
    timestamp = str(date).split()[0]
    return timestamp

#SCHEDULER MODULE. Parsing every day at 01:00 for the previous day's parsed post
schedule.every().day.at('01:00').do(analyze, get_str_date())
print('Scheduler up')

while True:
    print('check')
    schedule.run_pending()
    sleep(60)
analyze('2018-02-27')
