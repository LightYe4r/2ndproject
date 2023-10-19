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
from .serializer import UserSerializer, RoomSerializer, ReservationSerializer, FeedbackSerializer, PostSerializer,DayTimeTableSerializer
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
        data = request.data
        room_id = data.get('room_id')
        date = data.get('date')
        user_id = data.get('user_id')
        start = data.get('start')
        end = data.get('end')
        people_num = data.get('people_num')
        status = data.get('status')
        try:
            daytimetable = DayTimeTable.objects.filter(room_id = room_id, date = date)
            if(daytimetable.timetable[start:end+1] == '0' * (end - start)):
                daytimetable.timetable[start:end+1] = '1' * (end - start)
                reservation = Reservation.objects.create(room_id = room_id, date = date, user_id = user_id, start = start, end = end, people_num = people_num, status = status)
                reservation.save()
                daytimetable.save()
        except DayTimeTable.DoesNotExist:
            daytimetable = DayTimeTable.objects.create(room_id = room_id, date = date)
            daytimetable.timetable[start:end+1] = '1' * (end - start)
            reservation = Reservation.objects.create(room_id = room_id, date = date, user_id = user_id, start = start, end = end, people_num = people_num, status = status)
            reservation.save()
            daytimetable.save()
        serializer = DayTimeTableSerializer(daytimetable)  
        return Response(serializer.data)
    
class SearchDayTimeTable(APIView):  #request : { date : '20211012', start_time : 10, start_min : 30, usehour : 2 }
    def get(self, request, format=None, *args, **kwargs):
        data = request.data
        date = data.get('date')
        start = data.get('start')
        end = data.get('end')
        daytimetables = DayTimeTable.objects.filter(date = date)
        for daytimetable in daytimetables:
            if(daytimetable.timetable[start:end+1] == '0' * (end - start)):
                Rooms += Room.objects.get(id = daytimetable.room_id)
        serializer = RoomSerializer(Rooms, many=True)
        return Response(serializer.data)