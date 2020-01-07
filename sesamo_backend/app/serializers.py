from database.models import User, OfficialDocumentPic, FAQ, FAQCategory, Location
from rest_framework import serializers

# Serializers define the API representation.
class UserSerializer(serializers.ModelSerializer):
    profile_pic = serializers.ImageField(max_length=None, use_url=True, allow_null=True, required=False)
    class Meta:
        model = User
        fields = [
            'id',
            'email', 
            'first_name',
            'last_name',
            'CPF',
            'birthdate',
            'usertype',
            'sign_in_status',
            'user_code',
            'access_token',
            'is_staff',
            'profile_pic']

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
            'answer',
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
            'latitude',
            'longitude',
            'latitudeDelta',
            'longitudeDelta'
        ]