from django.shortcuts import render, redirect
from django.conf import settings
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from .models import User, Room, Reservation, Feedback, Post, DayTimeTable
from .serializer import UserSerializer, RoomSerializer, ReservationSerializer, FeedbackSerializer, PostSerializer
from django.http import JsonResponse
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from json.decoder import JSONDecodeError
from rest_framework import status


class Login(APIView):
    permission_classes = [AllowAny]
    def post(self, request, format=None, *args, **kwargs):
        data = request.data
        name = data.get('name')
        kakao_id = data.get('kakao_id')
        try:
            user = User.objects.get(name=name, kakao_id=kakao_id)
        except User.DoesNotExist:
            user = User.objects.create(name=name, kakao_id=kakao_id)
            user.save()
        token = TokenObtainPairSerializer.get_token(user)
        return Response({'refresh_token': str(token), 'token': str(token.access_token)})
    
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    
class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    
class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    
class RoomList(APIView):
    def get(self, request, format=None, *args, **kwargs):
        data = request.data
        type = data.get('type')
        rooms = Room.objects.filter(type = type)
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)

class RoomDetailView(APIView):
    def get(self, request, format=None, *args, **kwargs):
        room_id = kwargs.get('room_id')
        room = Room.objects.get(id = room_id)
        serializer = RoomSerializer(room)
        return Response(serializer.data)

class RoomReservation(APIView):
    def post(self, request, format=None, *args, **kwargs):
        check = True
        data = request.data
        room_id = data.get('room_id')
        date = data.get('day')
        start_time = data.get('start_time') * 2 + data.get('start_min') // 30 + data.get('pm') * 24
        usehour = data.get('usehour')
        people_num = data.get('people_num')
        room = Room.objects.get(id = room_id)
        if(people_num < room.people_num):
            return Response({'message': '인원수가 너무 적습니다.'})
        for i in range(usehour):
            if(room.timetable[start_time + i] == 1):
                check = False
                break
        if(check == False):
            return Response({'message': '이미 예약된 시간입니다.'})
        for i in range(usehour):
            room.timetable[start_time + i] = 1
        room.save()
        return Response({'message': '예약이 완료되었습니다.'})
    
    def get(self, request, format=None, *args, **kwargs):
        data = request.data
        room_id = data.get('room_id')
        date = data.get('day')
        room = Room.objects.get(id = room_id)
        daytimetable = DayTimeTable.objects.get(room_id = room_id, day = date)
        timetable = daytimetable.timetable
        return Response({'timetable': timetable})