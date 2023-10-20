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

"""request
{
    "username" : "test",
    "kakao_id" : "1234"
}
"""

class Login(APIView):
    permission_classes = [AllowAny]
    def post(self, request, format=None, *args, **kwargs):
        data = request.data
        username = data.get('username')
        kakao_id = data.get('kakao_id')
        try:
            user = User.objects.get(username=username, kakao_id=kakao_id)
        except User.DoesNotExist:
            user = User.objects.create(username=username, kakao_id=kakao_id)
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

"""request
{
    "room_id" : 1,
    "date" : "2023-10-12",
    "user_id" : 1,
    "start" : 10,
    "end" : 15,
    "people_num" : 2
}
"""
class RoomReservation(APIView):
    def post(self, request, format=None, *args, **kwargs):
        data = request.data
        room_id = data.get('room_id')
        date = data.get('date')
        user_id = data.get('user_id')
        start = data.get('start')
        end = data.get('end')
        people_num = data.get('people_num')
        room = Room.objects.get(id = room_id)
        user = User.objects.get(id = user_id)
        daytimetable = DayTimeTable.objects.get(room_id = room, date = date)
        if('1' not in daytimetable.timetable[start:end+1]):
            print(daytimetable.timetable[start:end+1])
            reserve = '1' * (end - start)
            daytimetable.timetable = daytimetable.timetable[:start] + reserve + daytimetable.timetable[end + 1:]
            reservation = Reservation.objects.create(room_id = room, date = date, user_id = user, start = start, end = end, people_num = people_num)
            reservation.save()
            serializer = ReservationSerializer(reservation)
            daytimetable.save()
        else:
            print("no")
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data)

"""request
{
    "date" : "2023-10-12",
    "type" : "smash"
}
"""


class SearchDayTable(APIView):
    def get(self, request, format=None, *args, **kwargs):
        data = request.data
        date = data.get('date')
        type = data.get('type')
        Rooms = Room.objects.filter(type = type)
        room_num = Rooms.count()
        table = [room_num]*26
        for room in Rooms:
            try:
                daytimetable = DayTimeTable.objects.get(room_id = room, date = date)
                for i in range(26):
                    if(daytimetable.timetable[i] == '1'):
                        table[i] -= 1
            except DayTimeTable.DoesNotExist:
                newdaytimetable = DayTimeTable.objects.create(room_id = room, date = date)
                newdaytimetable.save()
        return JsonResponse(table, safe=False)

"""request
{ 
    "date" : "2023-10-12",
    "type" : "smash",
    "start" : 10,
    "end" : 15
}
"""

class SearchDayTimeTable(APIView):  #request : { date : '20211012', start_time : 10, start_min : 30, usehour : 2 }
    def get(self, request, format=None, *args, **kwargs):
        data = request.data
        date = data.get('date')
        type = data.get('type')
        start = data.get('start')
        end = data.get('end')
        Rooms = Room.objects.filter(type = type)
        for room in Rooms:
            daytimetable = DayTimeTable.objects.get(room_id = room, date = date)
            if('1' in daytimetable.timetable[start:end+1]):
                Rooms = Rooms.exclude(id = room.id)
        serializer = RoomSerializer(Rooms, many=True)
        return Response(serializer.data)
    
class RoomControl(APIView):
    def post(self, request, format=None, *args, **kwargs):
        data = request.data
        room_id = data.get('room_id')
        date = data.get('date')
        start = data.get('start')
        end = data.get('end')
        command = data.get('command')
        if(room_id == 'all'):
            rooms = Room.objects.all()
            if(command == 'on'):
                for room in rooms:
                    try:
                        daytimetable = DayTimeTable.objects.get(room_id = room, date = date)
                        daytimetable.timetable[start:end+1] = '0' * (end - start)
                        daytimetable.save()
                    except DayTimeTable.DoesNotExist:
                        pass
                    room.status = 'on'
                    room.save()
            elif(command == 'off'):
                for room in rooms:
                    try:
                        daytimetable = DayTimeTable.objects.get(room_id = room, date = date)
                        daytimetable.delete()
                    except DayTimeTable.DoesNotExist:
                        pass
                    try:
                        reservation = Reservation.objects.get(room_id = room.id, date = date)
                        reservation.delete()
                    except Reservation.DoesNotExist:
                        pass
                    room.status = 'off'
                    room.save()
            serializer = RoomSerializer(rooms, many=True)
            return Response(serializer.data)
        else:
            room = Room.objects.get(id = room_id)
            if(command == 'on'):
                try:
                    daytimetable = DayTimeTable.objects.get(room_id = room_id, date = date)
                    daytimetable.timetable[start:end+1] = '0' * (end - start)
                    daytimetable.save()
                except DayTimeTable.DoesNotExist:
                    pass
                room.status = 'on'
                room.save()
            elif(command == 'off'):
                try:
                    daytimetable = DayTimeTable.objects.get(room_id = room_id, date = date)
                    daytimetable.delete()
                except DayTimeTable.DoesNotExist:
                    pass
                try:
                    reservation = Reservation.objects.get(room_id = room_id, date = date)
                    reservation.delete()
                except Reservation.DoesNotExist:
                    pass
                room.status = 'off'
                room.save()
            serializer = RoomSerializer(room)
            return Response(serializer.data)