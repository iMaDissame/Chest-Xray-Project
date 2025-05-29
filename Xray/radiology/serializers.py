from rest_framework import serializers
from django.contrib.auth.models import User
from .models import DocumentModel, DoctorsInfo

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')
        extra_kwargs = {'password': {'write_only': True}}
        
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user

class DoctorInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorsInfo
        fields = '__all__'

class DocumentModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentModel
        fields = '__all__'