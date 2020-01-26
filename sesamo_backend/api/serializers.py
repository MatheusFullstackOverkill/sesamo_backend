from .models import User, OfficialDocumentPic, FAQ, FAQCategory, Location
from rest_framework import serializers

# Serializers define the API representation.
class UserSerializer(serializers.ModelSerializer):
    profile_pic = serializers.ImageField(max_length=None, use_url=True, allow_null=True, required=False)
    class Meta:
        model = User
        fields = [
            'id',
            'email', 
            'full_name',
            'CPF',
            'cellphone',
            'birthdate',
            'usertype',
            'sign_in_status',
            'sign_in_date',
            'sign_review_date',
            'sign_validation_date',
            'user_code',
            'access_token',
            'is_staff',
            'profile_pic',
            'channel_name',
            'user_who_requested',
            'busy']

class UserCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_code']

class DocumentSerializer(serializers.ModelSerializer):
    document_pic = serializers.ImageField(max_length=None, use_url=True, allow_null=True, required=False)
    class Meta:
        model = OfficialDocumentPic
        fields = [
            # 'user_id',
            'document_type',
            'document_pic'
        ]

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = [
            'aunswer',
            'question'
        ]

class FAQCategorySerializer(serializers.ModelSerializer):
    questions = FAQSerializer(many=True, read_only=True)
    class Meta:
        model = FAQCategory
        fields = [
            # 'user_id',
            'name',
            'questions'
        ]

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = [
            'name',
            'description',
            'latitude',
            'longitude',
            'latitudeDelta',
            'longitudeDelta'
        ]