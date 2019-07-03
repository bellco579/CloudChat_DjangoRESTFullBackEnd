from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db.models import Q, Sum, Count
from django.http.response import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions
from rest_framework.parsers import JSONParser
from chat.models import Message, UserProfile
from chat.serializers import MessageSerializer, UserSerializer, RoomSerializers, UserProfileSerializer

import json

from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Room


class Rooms(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request):
        rooms = Room.objects.all()
        serializer = RoomSerializers(rooms, many=True)
        return Response({"data": serializer.data})


class Chat(APIView):
    permission_classes = [permissions.AllowAny, ]

    def get(self, request):
        sel_id = request.GET.get("sel")
        try:
            if sel_id[0] == "g":
                resiver = Room.objects.get(id=int(sel_id[1::]))
                message = resiver.message.all()
            else:
                resiver = User.objects.get(id=int(sel_id))
                message = Message.objects.filter(content_type__model="user", object_id=int(sel_id), sender=request.user) | Message.objects.filter(
                    content_type__model="user", sender=resiver,object_id=request.user.id)


            serializer = MessageSerializer(message, many=True)
            return Response({"data": serializer.data})

        except TypeError:
            chats = Room.objects.filter(invited=request.user)

            privateChat2 = Message.objects.filter(
                content_type__model="user", object_id=request.user.id) | \
                           Message.objects.filter(sender=request.user,
                                                  content_type__model="user")

            UserSet = set(chat_item.resiver for chat_item in privateChat2)

            userSerializer = UserSerializer(UserSet, many=True)
            roomSerializer = RoomSerializers(chats, many=True)

            return Response({
                "GroupChat": roomSerializer.data,
                "PrivateChat": userSerializer.data,
            })


def index(request):
    if request.user.is_authenticated:
        return redirect('chats')
    if request.method == 'GET':
        return render(request, 'chat/index.html', {})
    if request.method == "POST":
        username, password = request.POST['username'], request.POST['password']
        user = authenticate(username=username, password=password)
        print(user)
        if user is not None:
            login(request, user)
        else:
            return HttpResponse('{"error": "User does not exist"}')
        return redirect('chats')


@csrf_exempt
def user_list(request, pk=None):
    """
    List all required messages, or create a new message.
    """
    if request.method == 'GET':
        if pk:
            users = User.objects.filter(id=pk)
        else:
            users = User.objects.all()
        serializer = UserSerializer(users, many=True, context={'request': request})
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        try:
            user = User.objects.create_user(username=data['username'], password=data['password'])
            UserProfile.objects.create(user=user)
            return JsonResponse(data, status=201)
        except Exception:
            return JsonResponse({'error': "Something went wrong"}, status=400)


@csrf_exempt
def message_list(request, sender=None, receiver=None):
    """
    List all required messages, or create a new message.
    """
    if request.method == 'GET':
        messages = Message.objects.filter(sender_id=sender, receiver_id=receiver, is_read=False)
        serializer = MessageSerializer(messages, many=True, context={'request': request})
        for message in messages:
            message.is_read = True
            message.save()
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)


def register_view(request):
    """
    Render registration template
    """
    if request.user.is_authenticated:
        return redirect('chats')
    return render(request, 'chat/register.html', {})


def chat_view(request):
    if not request.user.is_authenticated:
        return redirect('index')
    if request.method == "GET":
        return render(request, 'chat/chat.html',
                      {'users': User.objects.exclude(username=request.user.username)})


def message_view(request, sender, receiver):
    if not request.user.is_authenticated:
        return redirect('index')
    if request.method == "GET":
        return render(request, "chat/messages.html",
                      {'users': User.objects.exclude(username=request.user.username),
                       'receiver': User.objects.get(id=receiver),
                       'messages': Message.objects.filter(sender_id=sender, receiver_id=receiver) |
                                   Message.objects.filter(sender_id=receiver, receiver_id=sender)})
