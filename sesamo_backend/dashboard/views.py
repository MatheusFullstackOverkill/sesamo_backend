from django.shortcuts import render
from database.models import User
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import UserSerializer
from django.utils.crypto import get_random_string
from django.http import HttpResponseNotFound, HttpResponseForbidden
from datetime import datetime, timezone
from django.core import serializers
import traceback
import json

# Create your views here.

# Middleware to check token
class CheckValidParamMixin(object):

    def dispatch(self, request, *args, **kwargs):
        # print(request.META['PATH_INFO'])
        if(request.META['PATH_INFO'] == '/app/users/login/'):
            return super(CheckValidParamMixin, self).dispatch(request, *args, **kwargs)
        # param = self.kwargs.get('param')
        # valid_param = is_valid_param(param)
        # try:
        #     data = User.objects.get(access_token=request.headers['Authorization'])
        #     return super(CheckValidParamMixin, self).dispatch(request, *args, **kwargs)
        # except:
        #     traceback.print_exc()
        #     return HttpResponseForbidden('Invalid token')

        try:
            data = User.objects.get(access_token=request.headers['Authorization'])
            now = datetime.now(timezone.utc)
            access_token_created_at = data.access_token_created_at
            if((now-access_token_created_at).total_seconds() >= 7200):
                data.access_token = ''
                data.access_token_created_at = ''
                data.save()
                return HttpResponseForbidden('Invalid token')
            else:
                return super(CheckValidParamMixin, self).dispatch(request, *args, **kwargs)
        except:
            traceback.print_exc()
            return HttpResponseForbidden('Token not found')

# ViewSets define the view behavior.
class UserViewSet(CheckValidParamMixin, viewsets.ViewSet):
    # queryset = User.objects.all()
    # serializer_class = UserSerializer

    def check_existing_token(self, token):
        try:
            data = User.objects.get(access_token=token)
            unique_id = get_random_string(length=32)
            self.check_existing_token(unique_id)
        except:
            return token

    @action(detail=True,methods=['post'])
    def login(self, request, *args, **kwargs):
        loginData = json.loads(request.body)
        print(loginData)
        try:
            data = User.objects.get(email=loginData['email'])
            if(data.check_password(loginData['password'])):
                unique_id = get_random_string(length=32)
                token = self.check_existing_token(unique_id)
                data.access_token = token
                data.access_token_created_at = datetime.now(timezone.utc)
                data.save()
                data = {
                    'userId': data.pk,
                    'token': token
                }
                return Response(data)
            else:
                print('Invalid password...')
                return Response('Invalid password', status=403)
        except:
            traceback.print_exc()
            print('User not found...')
            return Response('User not found', status=403)

    @action(detail=True, methods=['get'])
    def logout(self, request, *args, **kwargs):
        try:
            data = User.objects.get(access_token='5iltT5M4gVKhj39yuOB2ArXK0fXZuE3m')
            data.access_token = ''
            data.access_token_created_at = None
            data.save()
            return Response('Token deleted!')
        except:
            traceback.print_exc()
            return Response('Token not found')

    @action(detail=True, methods=['get'])
    def teste(self, request, *args, **kwargs):
        return Response(True)