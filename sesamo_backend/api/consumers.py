from channels.generic.websocket import WebsocketConsumer
from .pyrebase_config import *
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework.authtoken.models import Token
from urllib.parse import parse_qs
from asgiref.sync import async_to_sync
from math import sin, cos, sqrt, atan2, radians
from operator import attrgetter, itemgetter
from .models import *
import threading
import copy
import time

class ScanConsumer(WebsocketConsumer):
    def connect(self):
        print(self.scope['user'])
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

class PanicButtonConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        try:
            token_key = parse_qs(self.scope["query_string"].decode("utf8"))["token"][0]
            user = Token.objects.get(key=token_key).user
            self.scope["user"] = user
            print(self.scope["user"])
            self.scope['user'].channel_name = self.channel_name
            self.scope['user'].save()
            # Join room group
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )

            self.accept()

        except:
            self.disconnect()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        try:
            user_data = text_data_json['user_data']
            userType = 'user'
            user = user_data

        except:
            userType = 'employee'
            employee_data = text_data_json['employee_data']
            user = employee_data

        # locations = []
        locations_distance = []

        def add_to_locations_array(item_type, array_to_verify, array_to_add):
            for item in array_to_verify:
                # approximate radius of earth in km
                R = 6373.0

                lat1 = radians(user['latitude'])
                lon1 = radians(user['longitude'])
                lat2 = radians(item.latitude)
                lon2 = radians(item.longitude)

                dlon = lon2 - lon1
                dlat = lat2 - lat1

                a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
                c = 2 * atan2(sqrt(a), sqrt(1 - a))

                distance = R * c

                # locations.append(distance)
                array_to_add.append({
                    item_type: item,
                    'distance': distance
                })

        locations = Location.objects.all()
        
        add_to_locations_array('location', locations, locations_distance)
            
        closest_location = min(locations_distance, key=itemgetter('distance'))

        employee_confirmed = False

        def send_message():
                # Send message to single channel
                # Request to employee
            
            if employee_confirmed == False:

                employees_distance = []

                employees = User.objects.filter(workplace=closest_location['location'], busy=False)

                add_to_locations_array('user', employees, employees_distance)

                if len(employees_distance) > 0:
                    closest_employee = min(employees_distance, key=itemgetter('distance'))
                    closest_employee['user'].busy = True
                    closest_employee['user'].user_who_requested = User.objects.get(pk=user['user_id'])
                    closest_employee['user'].save()

                    async_to_sync(self.channel_layer.send)(
                        closest_employee['user'].channel_name,
                        {
                            'type': 'chat_message',
                            'message': json.dumps({
                                'user_data': user_data
                            })
                        }
                    )
                
                else:
                    inter.cancel()
                
        StartTime=time.time()

        class setInterval :
            def __init__(self,interval,action) :
                self.interval=interval
                self.action=action
                self.stopEvent=threading.Event()
                thread=threading.Thread(target=self.__setInterval)
                thread.start()

            def __setInterval(self) :
                nextTime=time.time()+self.interval
                while not self.stopEvent.wait(nextTime-time.time()) :
                    nextTime+=self.interval
                    self.action()

            def confirm(self) :
                employees = User.objects.filter(workplace=closest_location['location'],busy=True, user_who_requested = User.objects.get(pk=text_data_json['user_id']))
                employees.update(busy=False, user_who_requested=None)
                print(employees)
                employee = User.objects.get(pk=employee_data['user_id'])
                employee.busy = True
                employee.user_who_requested = User.objects.get(pk=text_data_json['user_id'])
                employee.save()
                print(employee)
                print('opa')
                self.stopEvent.set()

            def cancel(self) :
                if userType == 'employee':
                    employees = User.objects.filter(workplace=closest_location['location'],busy=True, user_who_requested = User.objects.get(pk=text_data_json['user_id']))
                    employees.update(busy=False, user_who_requested=None)
                elif employee_confirmed == False:
                    employees = User.objects.filter(workplace=closest_location['location'],busy=True, user_who_requested = User.objects.get(pk=user['user_id']))
                    employees.update(busy=False, user_who_requested=None)
                print('Done.')
                self.stopEvent.set()

        # start action every 0.6s
        inter=setInterval(10,send_message)

        # will stop interval in 30s
        t=threading.Timer(30,inter.cancel)

        if text_data_json['message_type'] == 'request':

            send_message()

            t.start()
            
            # Send message to room group
            # async_to_sync(self.channel_layer.group_send)(
            #     self.room_group_name,
            #     {
            #         'type': 'chat_message',
            #         'message': message
            #     }
            # )

        if text_data_json['message_type'] == 'confirm':
            employee_confirmed = True
            inter.confirm()
            async_to_sync(self.channel_layer.send)(
                text_data_json['user_channel_name'],
                {
                    'type': 'chat_message',
                    'message': json.dumps({
                        'employee_data': employee_data
                    })
                }
            )

        if text_data_json['message_type'] == 'location_update':
            async_to_sync(self.channel_layer.send)(
                text_data_json['send_to_channel_name'],
                {
                    'type': 'chat_message',
                    'message': json.dumps({
                        'user_data': user
                    })
                }
            )

        if text_data_json['message_type'] == 'finish_proccess':
            inter.cancel()
            async_to_sync(self.channel_layer.send)(
                text_data_json['send_to_channel_name'],
                {
                    'type': 'chat_message',
                    'message': json.dumps({
                        'employee_data': employee_data,
                        'message': 'Processo finalizado!'
                    })
                }
            )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))

