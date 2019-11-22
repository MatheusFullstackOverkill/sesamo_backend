from django.shortcuts import render
from django.conf.urls import url, include
from accounts.models import User
from .serializers import UserSerializer
from rest_framework import routers, serializers, viewsets
from rest_framework.response import Response
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import action
import json
import pyrebase 
config = {
    'apiKey': "AIzaSyDDp0Kbb1pmL6RDeWPT5SDXQ8hBNMt4FHc",
    'authDomain': "cesamo-162d1e.firebaseapp.com",
    'databaseURL': "https://cesamo-162d1e.firebaseio.com",
    'projectId': "cesamo-162d1e",
    'storageBucket': "cesamo-162d1e.appspot.com",
    'messagingSenderId': "944173613735",
    'appId': "1:944173613735:web:58ac614233b8b421f89182"
}
firebase = pyrebase.initialize_app(config)

# Create your views here.

# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class AppUsers(viewsets.ViewSet):
    # queryset = AppUser.objects.all()
    # serializer_class = AppUserSerializer

    @action(detail=False, methods=['get'])
    def get_users(self, request):
        users = firebase.database().child('/users').get().val()
        return Response(users)

    @action(detail=False, methods=['post'])
    def update_user_data(self, request):
        data = json.loads(request.body)
        try:
          firebase.database().child('/users/'+data['userUid']+'/'+data['itemToChange']).set(data['newValue'])
          return Response(data['itemToChange']+' alterado com sucesso!')
        except:
            print('Opa!')
            return Response(status=500)