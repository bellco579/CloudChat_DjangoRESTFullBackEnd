from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from chat.models import Message
from .models import Room, UserProfile

class UserSerializer(serializers.ModelSerializer):


    class Meta:
        model = User
        fields = ['id', 'username']


class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ['sender', 'message', 'timestamp']

class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = ['user', "message"]

class RoomSerializers(serializers.ModelSerializer):
    """Сериализация комнат чата"""
    creater = UserSerializer()
    invited = UserSerializer(many=True)
    class Meta:
        model = Room
        fields = ("id", "creater", "invited", "date")