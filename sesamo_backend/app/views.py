from django.shortcuts import render
from database.models import User, OfficialDocumentPic, SituationalDocumentPic, FAQCategory, FAQ, Location
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import UserSerializer, DocumentSerializer, FAQCategorySerializer, FAQSerializer, LocationSerializer
from django.utils.crypto import get_random_string
from django.core.files.base import ContentFile
from datetime import datetime, timezone
from django.utils.dateparse import parse_datetime, parse_date
import traceback
import base64
import copy
import json
from django.http import HttpResponseNotFound, HttpResponseForbidden

# class SimpleMiddleware(object):
#     def __init__(self, get_response):
#         self.get_response = get_response
#         # One-time configuration and initialization.

#     def __call__(self, request):
#         print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
#         # Code to be executed for each request before
#         # the view (and later middleware) are called.

#         response = self.get_response(request)

#         # Code to be executed for each request/response after
#         # the view is called.

#         return response

# Middleware to check token
class CheckValidParamMixin(object):

    def dispatch(self, request, *args, **kwargs):
        # print(request.META['PATH_INFO'])
        if(request.META['PATH_INFO'] == '/app/users/login/') or (request.META['PATH_INFO'] == '/app/users/sign_in/') or (request.META['PATH_INFO'] == '/app/users/check_if_user_exists/'):
            return super(CheckValidParamMixin, self).dispatch(request, *args, **kwargs)
        # param = self.kwargs.get('param')
        # valid_param = is_valid_param(param)
        try:
            data = User.objects.get(access_token=request.headers['Authorization'])
            return super(CheckValidParamMixin, self).dispatch(request, *args, **kwargs)
        except:
            traceback.print_exc()
            return HttpResponseForbidden('Invalid token')

# Create your views here.

# ViewSets define the view behavior.
class UserViewSet(viewsets.ViewSet):
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
                # data.access_token_created_at = datetime.now(timezone.utc)
                data.access_token_created_at = datetime.now()
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
    def user_data(self, request, pk):
        userId = request.GET.get('userId')
        print(datetime.strptime('12/12/1999', "%d/%m/%Y").date())
        try:
            data = User.objects.get(pk=userId)
            serializer = UserSerializer(data, context={"request":request})
            print(serializer.data)
            userData = serializer.data
            return Response(userData)
        except:
            traceback.print_exc()
            return Response('User not found', status=404)

    @action(detail=True, methods=['post'])
    def update_user_data(self, request, pk):
        user_data = json.loads(request.body)
        try:
            user = User.objects.filter(pk=user_data['userId'])
            if(user):
                print(user)
                del user_data['userId']
                print(user_data)
                user.update(**user_data)
                return Response(True)
            else:
                return Response('User not found', status=404)
        except:
            traceback.print_exc()
            return Response(status=500)
    
    @action(detail=True, methods=['post'])
    def update_profile_pic(self, request, pk):
        data = json.loads(request.body)
        try:
            pic = data['pic']
            format, imgstr = pic.split(";base64,")
            ext = format.split("/")[-1]
            print(ext)
            image = ContentFile(base64.b64decode(imgstr), name="profile_pic." + ext)
            print(image.name)
            data = User.objects.get(pk=data['userId'])
            data.profile_pic = image
            data.save()
            serializer = UserSerializer(data, context={"request":request})
            print(serializer.data['profile_pic'])
            return Response(serializer.data['profile_pic'])
        except:
            traceback.print_exc()
            return Response(status=500)

    @action(detail=True, methods=['get'])
    def check_if_user_exists(self, request, pk):
        try:
            checkUser = User.objects.get(email=request.GET.get('email'))
            return Response('Email already in use', status=403)
        except:
            try:
                checkUser = User.objects.get(CPF=request.GET.get('CPF'))
                return Response('CPF already in use', status=403)
            except:
                return Response(True)

    @action(detail=True, methods=['get','post'])
    def sign_in(self, request, pk):
        # print(json.loads(request.body))
        signInData = json.loads(request.body)
        # try:
        print(signInData)
        print('phase' in signInData)
        if('phase' in signInData == False):
            newUser = User.objects.create_user(
                first_name=signInData['first_name'],
                last_name=signInData['last_name'],
                email=signInData['email'], 
                password=signInData['password'], 
                usertype=signInData['usertype'],
                CPF=signInData['CPF'],
                birthdate=datetime.strptime(signInData['birthdate'], "%d/%m/%Y").date(),
                sign_in_status=signInData['sign_in_status'],
                user_code=signInData['user_code'])
            return Response('User created!')
        elif(signInData['phase'] == 'update_profile_pic'):
            pic = signInData['pic']
            format, imgstr = pic.split(";base64,")
            ext = format.split("/")[-1]
            print(ext)
            image = ContentFile(base64.b64decode(imgstr), name="profile_pic." + ext)
            print(image.name)
            data = User.objects.get(pk=signInData['userId'])
            data.profile_pic = image
            data.sign_in_status = 2
            data.save()
            serializer = UserSerializer(data, context={"request":request})
            print(serializer.data['profile_pic'])
            return Response(serializer.data['profile_pic'])

        elif(signInData['phase'] == 'update_official_document'):
            for pic in signInData['picSet']:
                # print(signInData['document_type'])
                format, imgstr = pic['document'].split(";base64,")
                ext = format.split("/")[-1]
                print(ext)
                image = ContentFile(base64.b64decode(imgstr), name=pic['document_type']+"." + ext)
                print(image.name)
                document = OfficialDocumentPic(
                    user_id=User.objects.get(pk=signInData['userId']),
                    document_type=pic['document_type'],
                    document_pic=image)
                document.save()
            # print(OfficialDocumentPic.objects.filter(user_id=data['userId']))
            user = User.objects.get(pk=signInData['userId'])
            user.sign_in_status = 3
            user.save()
            data = OfficialDocumentPic.objects.filter(user_id=signInData['userId'])
            serializer = DocumentSerializer(data, many=True, context={"request":request})
            print(serializer.data)
            return Response(serializer.data)

        elif(signInData['phase'] == 'update_situatial_document'):
            pic = signInData['pic']
            print(pic['document_type'])
            format, imgstr = pic['document'].split(";base64,")
            ext = format.split("/")[-1]
            print(ext)
            image = ContentFile(base64.b64decode(imgstr), name=pic['document_type']+"." + ext)
            print(image.name)
            document = SituationalDocumentPic(
                user_id=User.objects.get(pk=signInData['userId']),
                document_type=pic['document_type'],
                document_pic=image)
            document.save()
            # print(OfficialDocumentPic.objects.filter(user_id=data['userId']))
            user = User.objects.get(pk=signInData['userId'])
            user.sign_in_status = 4
            user.sign_in_date = datetime.now()
            user.save()
            data = SituationalDocumentPic.objects.filter(user_id=signInData['userId'])
            serializer = DocumentSerializer(data, many=True, context={"request":request})
            print(serializer.data)
            response = serializer.data[0]
            return Response(response)
    # except:
    #     traceback.print_exc()
    #     return Response('User already exists', status=500)

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

class FAQViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['get'])
    def faq(self, request):
        faq = FAQCategory.objects.all()
        for category in faq:
            questions = FAQ.objects.filter(category=category).exclude(answer='')
            category.questions = questions
        # print(faq)
        serializer = FAQCategorySerializer(faq, many=True)
        # print(serializer.data)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def post_question(self, request, pk):
        data = json.loads(request.body)
        try:
            category=FAQCategory.objects.get(pk=data['categoryId'])
            newQuestion = FAQ(
                question=data['question'],
                category=category
            )
            newQuestion.save()
            return Response(True)
        except:
            traceback.print_exc()
            return Response('error', status=500)

class LocationsViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['get'])
    def locations(self, request):
        locations = Location.objects.all()
        # print(faq)
        serializer = LocationSerializer(locations, many=True)
        # print(serializer.data)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_location(self, request, pk):
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