from channels.generic.websocket import WebsocketConsumer
from .pyrebase_config import *
import json

class ScanConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        # text_data_json = json.loads(text_data)
        # message = text_data_json['message']
        data = json.loads(text_data)
        db = firebase.database()
        if data['bathroom_id'].isdigit() == False:
            self.send(text_data=json.dumps({
                'message': json.dumps({'error': 'Código inválido.'})
            }))
            self.disconnect()
        userCode = db.child(''.join(('/userCodes/',data['user_code']))).get().val()
        bathroom = db.child("bathrooms").child(data['bathroom_id']).get().val()
        if userCode != None and bathroom != None:
            if bathroom["inUse"] == True:
                    self.send(text_data=json.dumps({
                        'message': json.dumps(bathroom)
                    }))
                    self.disconnect()
            db.child("bathrooms").child(data['bathroom_id']).update({"userRequested": True})
            def listen_to_data_change(message):
                print(message["event"]) # put
                print(message["path"]) # /-K7yGTTEp7O549EzTYtI
                print(message["data"]) # {'title': 'Pyrebase', "body": "etc..."}
                if message["path"] == '/userVerified' and message["data"] == True:
                    self.send(text_data=json.dumps({
                        'message': json.dumps(bathroom)
                    }))
                    self.disconnect()

            my_stream = db.child(''.join(('/bathrooms/',data['bathroom_id']))).stream(listen_to_data_change)
        
        self.send(text_data=json.dumps({
            'message': json.dumps({'error': 'Ocorreu um erro.'})
        }))
        self.disconnect()

