from pymongo import MongoClient
from websocket import WebSocket
from json import dumps
import schedule
import time

true = True
false = False
null = None

def update():
    db = MongoClient('213.183.48.116').golos
    ws = WebSocket()
    ws.connect('wss://api.golos.cf')
    print('Starting update')
    for post in db.posts.find():
        ws.send(dumps({"id":1,"method":"get_content","params":[post['author'],post['permlink']]}))
        ids = post['id']
        response = eval(ws.recv())['result']
        db.posts.update({'id' : ids},{'$set':{'reward':response['pending_payout_value'], 'votes': response['net_votes'], 'comments': response['children']}})
        print('Updated post'+str(ids))

update()
schedule.every().hour.do(update)

while True:
    schedule.run_pending()
    time.sleep(30)



