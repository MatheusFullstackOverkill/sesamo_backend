from django.shortcuts import render
from .models import User, OfficialDocumentPic, SituationalDocumentPic, FAQCategory, FAQ, Location
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from .serializers import UserSerializer, DocumentSerializer, FAQCategorySerializer, FAQSerializer, LocationSerializer, UserCodeSerializer
from django.utils.crypto import get_random_string
from django.core.files.base import ContentFile
from datetime import datetime, timezone
from django.utils.dateparse import parse_datetime, parse_date
from django.http import HttpResponseNotFound, HttpResponseForbidden
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from pathlib import Path
import traceback
import base64
import copy
import json
import os
# from .password_token_validation import ForgotPasswordTokenAuthentication
from cryptography.fernet import Fernet
# from .fernet_key import f, key

# from rest_framework.permissions 
from rest_framework.authentication import TokenAuthentication
from .pyrebase_config import *

# Middleware to check token
# class CheckValidParamMixin(object):

#     def dispatch(self, request, *args, **kwargs):
#         # print(request.META['PATH_INFO'])
#         if(request.META['PATH_INFO'] == '/app/users/login/') or (request.META['PATH_INFO'] == '/app/users/sign_in/') or (request.META['PATH_INFO'] == '/app/users/check_if_user_exists/'):
#             return super(CheckValidParamMixin, self).dispatch(request, *args, **kwargs)
#         # param = self.kwargs.get('param')
#         # valid_param = is_valid_param(param)
#         try:
#             data = User.objects.get(access_token=request.headers['Authorization'])
#             return super(CheckValidParamMixin, self).dispatch(request, *args, **kwargs)
#         except:
#             traceback.print_exc()
#             return HttpResponseForbidden('Invalid token')

# # Middleware to check token and expiration date
# class CheckValidParamMixin(object):

#     def dispatch(self, request, *args, **kwargs):
#         # print(request.META['PATH_INFO'])
#         if(request.META['PATH_INFO'] == '/app/users/login/'):
#             return super(CheckValidParamMixin, self).dispatch(request, *args, **kwargs)
#         # param = self.kwargs.get('param')
#         # valid_param = is_valid_param(param)
#         # try:
#         #     data = User.objects.get(access_token=request.headers['Authorization'])
#         #     return super(CheckValidParamMixin, self).dispatch(request, *args, **kwargs)
#         # except:
#         #     traceback.print_exc()
#         #     return HttpResponseForbidden('Invalid token')

#         try:
#             data = User.objects.get(access_token=request.headers['Authorization'])
#             now = datetime.now(timezone.utc)
#             access_token_created_at = data.access_token_created_at
#             if((now-access_token_created_at).total_seconds() >= 7200):
#                 data.access_token = ''
#                 data.access_token_created_at = ''
#                 data.save()
#                 return HttpResponseForbidden('Invalid token')
#             else:
#                 return super(CheckValidParamMixin, self).dispatch(request, *args, **kwargs)
#         except:
#             traceback.print_exc()
#             return HttpResponseForbidden('Token not found')

# Create your views here.

# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):

    # permission_classes = (AllowAny,)

    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=True, methods=['post'])
    def update_user_data(self, request, pk):

        user_data = json.loads(request.body)
        try:
            userFromGet = User.objects.get(pk=pk)
            if 'profile_pic' in user_data:
                pic = user_data['profile_pic']
                format, imgstr = pic.split(";base64,")
                ext = format.split("/")[-1]
                image = ContentFile(base64.b64decode(imgstr), name="profile_pic." + ext)
                projetPath = str(os.path.join(os.path.abspath(os.path.dirname(__name__)) ))
                path = str(userFromGet.profile_pic.url)
                os.unlink(''.join((projetPath, path)).replace("\\", "/"))
                userFromGet.profile_pic.delete(save=True)
                userFromGet.profile_pic = image
                userFromGet.save()
                user_data.pop('profile_pic')
            if 'password' in user_data:
                userFromGet.set_password(user_data['password'])
                userFromGet.save()
                user_data.pop('password')
            userFromFilter = User.objects.filter(pk=pk)
            userFromFilter.update(**user_data)
            serializer = UserSerializer(userFromGet, context={"request":request}, partial=True)
            return Response(serializer.data)
        except:
            traceback.print_exc()
            return Response(status=500)

    @action(detail=False, methods=['post'], permission_classes=(AllowAny,))
    def check_if_user_exists(self, request, pk=None):
        data = json.loads(request.body)
        try:
            checkUser = User.objects.get(email = data['email'])
            response = {
                'error': 'Email já cadastrado.'
            }
            return Response(response, status=403)
        except:
            try:
                checkUser = User.objects.get(CPF = data['CPF'])
                response = {
                    'error': 'CPF já cadastrado.'
                }
                return Response(response, status=403)
            except:
                return Response(True)

    @action(detail=False, methods=['get'], permission_classes=(AllowAny,))
    def get_user_codes(self, request):
        users = User.objects.all().values('user_code')
        print(users)
        serializer = UserCodeSerializer(users, partial=True, many=True)
        user_codes = serializer.data
        print(self.queryset.values_list('user_code', flat=True))
        # for i in user_codes.values():
        #     print(i)
        return Response(self.queryset.values_list('user_code', flat=True))

    @action(detail=False, methods=['post'], permission_classes=(AllowAny,))
    def sign_in(self, request):
        signInData = json.loads(request.body)
        try:
            newUser = User.objects.create_user(
                full_name=signInData['full_name'],
                # last_name=signInData['last_name'],
                email=signInData['email'], 
                password=signInData['password'], 
                usertype=signInData['usertype'],
                CPF=signInData['CPF'],
                cellphone=signInData['cellphone'],
                birthdate=datetime.strptime(signInData['birthdate'], "%d/%m/%Y").date(),
                sign_in_status=signInData['sign_in_status'],
                user_code=signInData['user_code'])
            userId = {
                'userId' : newUser.id
            }
            return Response(userId)
        except:
            traceback.print_exc()
            return Response(status=500)

    @action(detail=True, methods=['post'])
    def add_user_profile_pic(self, request, pk):
        signInData = json.loads(request.body)
        try:
            pic = signInData['pic']
            format, imgstr = pic.split(";base64,")
            ext = format.split("/")[-1]
            print(ext)
            image = ContentFile(base64.b64decode(imgstr), name="profile_pic." + ext)
            print(image.name)
            data = User.objects.get(pk=pk)
            data.profile_pic = image
            data.sign_in_status = 2
            data.save()
            serializer = UserSerializer(data, context={"request":request})
            print(serializer.data['profile_pic'])
            return Response(serializer.data['profile_pic'])
        except:
            traceback.print_exc()
            return Response(status=500)

    @action(detail=True, methods=['post'])
    def add_user_official_document(self, request, pk):
        signInData = json.loads(request.body)
        try:
            pic = signInData['pic']
            # for pic in signInData['picSet']:
            # print(signInData['document_type'])
            format, imgstr = pic['document'].split(";base64,")
            ext = format.split("/")[-1]
            print(ext)
            image = ContentFile(base64.b64decode(imgstr), name=pic['document_type']+"." + ext)
            print(image.name)
            document = OfficialDocumentPic(
                user_id=User.objects.get(pk=pk),
                document_type=pic['document_type'],
                document_pic=image)
            document.save()
            # print(OfficialDocumentPic.objects.filter(user_id=data['userId']))
            user = User.objects.get(pk=pk)
            user.sign_in_status = 3
            user.save()
            data = OfficialDocumentPic.objects.filter(user_id=pk)
            serializer = DocumentSerializer(data, many=True, context={"request":request})
            print(serializer.data)
            return Response(serializer.data)
        except:
            traceback.print_exc()
            return Response(status=500)

    @action(detail=True, methods=['post'])
    def add_user_situacional_document(self, request, pk):
        signInData = json.loads(request.body)
        try:
            pic = signInData['pic']
            print(pic['document_type'])
            format, imgstr = pic['document'].split(";base64,")
            ext = format.split("/")[-1]
            print(ext)
            image = ContentFile(base64.b64decode(imgstr), name=pic['document_type']+"." + ext)
            print(image.name)
            document = SituationalDocumentPic(
                user_id=User.objects.get(pk=pk),
                document_type=pic['document_type'],
                document_pic=image)
            document.save()
            # print(OfficialDocumentPic.objects.filter(user_id=data['userId']))
            user = User.objects.get(pk=pk)
            user.sign_in_status = 4
            user.sign_in_date = datetime.now()
            user.save()
            data = SituationalDocumentPic.objects.filter(user_id=pk)
            serializer = DocumentSerializer(data, many=True, context={"request":request})
            print(serializer.data)
            response = serializer.data[0]
            return Response(response)
        except:
            traceback.print_exc()
            return Response(status=500)
    # except:
    #     traceback.print_exc()
    #     return Response('User already exists', status=500)

    @action(detail=True, methods=['get'])
    def activate_user(self, request, pk):
        try:
            data = User.objects.get(pk=pk)
            data.sign_in_status = 7
            data.save()
            return Response('User activated!')
        except:
            traceback.print_exc()
            return Response('User not found', status=404)

    @action(detail=False, methods=['get'])
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

class FAQViewSet(viewsets.ModelViewSet):

    queryset = FAQCategory.objects.all()

    def get_queryset(self):
        queryset = FAQCategory.objects.all()
        for category in queryset:
            questions = FAQ.objects.filter(category=category).exclude(aunswer='')
            category.questions = questions
        return queryset
        
    serializer_class = FAQCategorySerializer

    @action(detail=False, methods=['get'])
    def all(self, request):
        faq = FAQCategory.objects.all()
        for category in faq:
            questions = FAQ.objects.filter(category=category)
            category.questions = questions
        # print(faq)
        serializer = FAQCategorySerializer(faq, many=True)
        # print(serializer.data)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def post_question(self, request, pk):
        data = json.loads(request.body)
        try:
            category=FAQCategory.objects.get(pk=pk)
            newQuestion = FAQ(
                question=data['question'],
                category=category
            )
            newQuestion.save()
            return Response(True)
        except:
            traceback.print_exc()
            return Response('error', status=500)

class QuestionsViewSet(viewsets.ModelViewSet):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer

class LocationsViewSet(viewsets.ModelViewSet):

    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    @action(detail=False, methods=['post'])
    def add_location(self, request):
        data = json.loads(request.body)
        try:
            newLocation = Location(
                name = data['name'],
                latitude = data['latitude'],
                longitude = data['longitude'],
                latitudeDelta = data['latitudeDelta'],
                longitudeDelta = data['longitudeDelta']
            )
            newLocation.save()
            return Response(True)
        except:
            traceback.print_exc()
            return Response('error', status=500)

def reset_password(request):
    return render(request, 'reset_password.html')

# class ScanQRCode(APIView):
#     def get(self, request, format=None):
#         db = firebase.database()
#         userCodes = db.child(''.join(('/userCodes/','171662225'))).get()
#         print(userCodes.val())
#         if userCodes.val() != None:
#             print('opa')
#         return Response(True) 

#     def post(self, request, format=None):
#         data = json.loads(request.body)
#         db = firebase.database()
#         userCode = db.child(''.join(('/userCodes/',data['user_code']))).get().val()
#         print(userCode)
#         if userCode != None:
#             db.child("bathrooms").child(data['bathroom_id']).update({"userRequested": True})
#             def listen_to_data_change(message):
#                 print(message["event"]) # put
#                 print(message["path"]) # /-K7yGTTEp7O549EzTYtI
#                 print(message["data"]) # {'title': 'Pyrebase', "body": "etc..."}
#                 return Response(True)

#             my_stream = db.child(''.join(('/userCodes/',data['user_code']))).stream(listen_to_data_change)
#         return Response(True) 

# class ForgotPasswordViewSet(viewsets.ViewSet):

#     # permission_classes=(AllowAny,)
#     authentication_classes=(ForgotPasswordTokenAuthentication,)

#     @action(detail=False, methods=['post'], permission_classes=(AllowAny,))
#     def create_new_password_token(self, request):
#         data = json.loads(request.body)
#         email = data['email']
#         user = User.objects.get(email=email)
#         byte_str = bytes(email, encoding="utf-8")
#         token = f.encrypt(byte_str).decode(encoding="utf-8")
#         # email_decrypted = f.decrypt(bytes(token, encoding="utf-8")).decode(encoding="utf-8")
#         # user = User.objects.get(email=email_decrypted)
#         # user.forgot_password_token = token
#         # user.forgot_password_token_created_at = datetime.now(timezone.utc)
#         # user.save()
#         return Response({'forgot_password_token':token})

#     @action(detail=False, methods=['get'])
#     def verify_token(self, request):
#         print(request.user.first_name)
#         return Response({'message': 'Valid token!'})

