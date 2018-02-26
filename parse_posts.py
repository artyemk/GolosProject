from websocket import WebSocket
from pymongo import MongoClient
import json
import re

#preventing eval mistakes
true = True
false = False
null = None

#connecting to db for posts and blockchain websocket
db = MongoClient().golos
ws = WebSocket()
ws.connect('wss://api.golos.cf')

print('Sending for 100')

#Sending query to fetch last 100 posts
ws.send(json.dumps({"id":6,"method":"get_discussions_by_created","params":[{"tag":"","limit":"100"}]}))
post = eval(ws.recv())['result'][0]

#get needed params and dump in db
for i in range(len(post)):
    ids = post['id']
    write = dump = {'id': ids,
       'author': post['author'],
       'permlink': post['permlink'],
       'timestamp': post['created'].split('T')[0],
       'title': post['title'],
       'body': re.sub(r"<.*?>",' ',post['body']),
       'tags': eval(post['json_metadata'])['tags']
       }
    db.posts.insert_one(write)
print('Got 100, going in WHILE')


#parsing stream of new articles
while(True):
    #first var without except
    try:
        ids = post['id']
    except Exception:
        pass
    #getting info on last post
    ws.send(json.dumps({"id":6,"method":"get_discussions_by_created","params":[{"tag":"","limit":"1"}]}))
    post = eval(ws.recv())['result'][0]
    #check for new post
    if ids != post['id']:
        print('Got new one')
        #if id chaged get params and dump in db
        write ={'id': ids,
                'author': post['author'],
                'permlink': post['permlink'],
                'timestamp': post['created'].split('T')[0],
                'title': post['title'],
                'body': re.sub(r"<.*?>",' ',post['body']),
                'tags': eval(post['json_metadata'])['tags']
                }
        print(post['title'])
        print(post['created'])
        db.posts.insert_one(write)
