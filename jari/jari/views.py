from django.shortcuts import render, redirect
from django.conf import settings
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from .models import *
from .serializer import *
# from .models import User, Room, Reservation, Feedback, Post, DayTimeTable
# from .serializer import UserSerializer, RoomSerializer, ReservationSerializer, FeedbackSerializer, PostSerializer,DayTimeTableSerializer, MyPageSerializer
from django.http import JsonResponse
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from json.decoder import JSONDecodeError
from rest_framework import status
import json

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
    
"""request
{
    "date" : "2023-10-12",
    "type" : "smash"
}
"""
    
class SearchDayTable(APIView):
    def get(self, request, format=None, date = None, type = None):
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

class SearchDayTimeTable(APIView): 
    def get(self, request, format=None, date = None, type = None, start = None, end = None):
        Rooms = Room.objects.filter(type = type)
        for room in Rooms:
            daytimetable = DayTimeTable.objects.get(room_id = room, date = date)
            if('1' in daytimetable.timetable[start:end+1]):
                Rooms = Rooms.exclude(id = room.id)
        serializer = RoomSerializer(Rooms, many=True)
        return Response(serializer.data)

class SearchDayTimeTables(APIView):
    def get(self, request, format=None, date = None):
        DayTimeTables = DayTimeTable.objects.filter(date = date)
        serializer = DayTimeTableSerializer(DayTimeTables, many=True)
        return Response(serializer.data)
    
"""request
{
    "room_name" : "smash0",
    "date" : "2023-10-12"
}
"""
class SearchRoomTimeTable(APIView):
    def get(self, request, format=None, room_name = None, date = None):
        room = Room.objects.get(name = room_name)
        daytimetable = DayTimeTable.objects.get(room_id = room, date = date)
        serializer = DayTimeTableSerializer(daytimetable)
        return Response(serializer.data)
    
"""request
{
    "room_name" : "smash0",
    "date" : "2023-10-12",
    "kakao_id" : 1,
    "start" : 10,
    "end" : 15,
    "people_num" : 2
}
"""
class RoomReservation(APIView):
    def post(self, request, format=None, *args, **kwargs):
        data = request.data
        room_name = data.get('room_name')
        date = data.get('date')
        kakao_id = data.get('kakao_id')
        start = data.get('start')
        end = data.get('end')
        people_num = data.get('people_num')
        room = Room.objects.get(name = room_name)
        user = User.objects.get(kakao_id = kakao_id)
        try:
            reservation = Reservation.objects.get(date = date, user_id = user)
            serializer = ReservationSerializer(reservation)
            return Response(serializer.data)
        except Reservation.DoesNotExist:
            daytimetable = DayTimeTable.objects.get(room_id = room, date = date)
            if('1' not in daytimetable.timetable[start:end+1]):
                reserve = '1' * (end - start +1 )
                daytimetable.timetable = daytimetable.timetable[:start] + reserve + daytimetable.timetable[end + 1:]
                reservation = Reservation.objects.create(room_id = room, date = date, user_id = user, start = start, end = end, people_num = people_num)
                reservation.save()
                serializer = ReservationSerializer(reservation)
                daytimetable.save()
            else:
                serializer = DayTimeTableSerializer(daytimetable)
                return Response(serializer.data)
            return Response(serializer.data)

"""request
{
    "kakao_id" : 1
}
"""

class ReservationList(APIView):
    def get(self, request, format=None, kakao_id = None):
        user = User.objects.get(kako_id = kakao_id)
        reservations = Reservation.objects.filter(user_id = user)
        serializer = ReservationSerializer(reservations, many=True)
        return Response(serializer.data)
    
"""request
{
    "room_name" : "smash0",
    "date" : "2023-10-12",
    "kakao_id" : "1234"
}
"""
class DeleteReservation(APIView):
    def post(self, request, format=None, *args, **kwargs):
        data = request.data
        room_name = data.get('room_name')
        date = data.get('date')
        kakao_id = data.get('kakao_id')
        room = Room.objects.get(name = room_name)
        user = User.objects.get(kakao_id = kakao_id)
        reservation = Reservation.objects.get(room_id = room, date = date, user_id = user)
        start = reservation.start
        end = reservation.end
        daytimetable = DayTimeTable.objects.get(room_id = room, date = date)
        reserve = '0' * (end - start)
        daytimetable.timetable = daytimetable.timetable[:start] + reserve + daytimetable.timetable[end + 1:]
        daytimetable.save()
        reservation.delete()
        serializer = DayTimeTableSerializer(daytimetable)
        return Response(serializer.data)
    
"""request
{
    "room_name" : "smash0",
    "date" : "2023-10-12",
    "kakao_id" : "1234"
}
"""
class ExtendReservation(APIView):
    def post(self, request, format=None, *args, **kwargs):
        data = request.data
        room_name = data.get('room_name')
        date = data.get('date')
        kakao_id = data.get('kakao_id')
        room = Room.objects.get(name = room_name)
        user = User.objects.get(kakao_id = kakao_id)
        reservation = Reservation.objects.get(room_id = room, date = date, user_id = user)
        extension = reservation.extension
        if(extension > 0):
            end = reservation.end
            daytimetable = DayTimeTable.objects.get(room_id = room, date = date)
            if('1' not in daytimetable.timetable[end+1:end+2]):
                reserve = '1' * 1
                daytimetable.timetable = daytimetable.timetable[:end+1] + reserve + daytimetable.timetable[end + 2:]
                reservation.end += 1
                reservation.extension -= 1
                daytimetable.save()
                reservation.save()
                serializer = ReservationSerializer(reservation)
                return Response(serializer.data)
            else:   # 이미 예약이 있는 경우
                serializer = DayTimeTableSerializer(daytimetable)
                return Response(serializer.data)
        else:   # 연장 횟수를 다 쓴 경우
            return Response(extension)
    def get(self, request, format=None, reservation_id = None):
        reservation = Reservation.objects.get(id = reservation_id)
        extension = reservation.extension
        return Response(extension)
    
    """request
    {
    
    }"""
class RefreshTokenView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        refresh = request.data.get('refresh_token')

        if not refresh:
            return Response({'error': 'Refresh token이 제공되지 않았습니다.'}, status=status.HTTP_BAD_REQUEST)

        try:
            refresh_token = RefreshToken(refresh)
            access_token = refresh_token.access_token
            return Response({'access_token': str(access_token)}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': '유효하지 않은 refresh token입니다.'}, status=status.HTTP_BAD_REQUEST)
"""request
{
    "kakao_id" : "1234",
    "date" : "2023-11-07"
}"""
class SearchMyReservation(APIView):
    def post(self, request, format=None):
        data = request.data 
        kakao_id = data.get('kakao_id')
        date = data.get('date')
        user = User.objects.get(kakao_id = kakao_id)
        reservations = Reservation.objects.filter(user_id = user, date = date)
        room = reservations[0].room_id
        daytimetable = DayTimeTable.objects.filter(date = date, room_id = room)
        serializer = MyPageSerializer({"reservations": reservations, "daytimetable": daytimetable})
        return Response(serializer.data)
    
"""request
{
    "room_name" : "smash0",
    "kakao_id" : "1234",
    "content" : "test"
}"""
    
class MakeFeedback(APIView):
    def post(self, request, format=None):
        data = request.data
        mode = data.get('mode')
        if(mode == 'create'): # 피드백 생성, room_name, kakao_id, content, case 필요
            room_name = data.get('room_name')
            kakao_id = data.get('kakao_id')
            content = data.get('content')
            case = data.get('case')
            room = Room.objects.get(name = room_name)
            user = User.objects.get(kakao_id = kakao_id)
            feedback = Feedback.objects.create(room_id = room, user_id = user, content = content, case = case)
            feedback.save()
            serializer = FeedbackSerializer(feedback)
            return Response(serializer.data)
        
        elif(mode == 'read'): # 피드백 조회, room_name or kakao_id or status or feedback_id or case 필요
            room_name = data.get('room_name')
            kakao_id = data.get('kakao_id')
            status = data.get('status')
            feedback_id = data.get('feedback_id')
            case = data.get('case')
            if(room_name):
                room = Room.objects.get(name = room_name)
                feedbacks = Feedback.objects.filter(room_id = room)
            elif(kakao_id):
                user = User.objects.get(kakao_id = kakao_id)
                feedbacks = Feedback.objects.filter(user_id = user)
            elif(status):
                feedbacks = Feedback.objects.filter(status = status)
            elif(feedback_id):
                feedbacks = Feedback.objects.filter(feedback_id = feedback_id)
            elif(case):
                feedbacks = Feedback.objects.filter(case = case)
            else:
                feedbacks = Feedback.objects.all()
            serializer = FeedbackSerializer(feedbacks, many=True)
            return Response(serializer.data)
        
        elif(mode == 'update'): # 피드백 수정, feedback_id, content, case 필요
            feedback_id = data.get('feedback_id')
            content = data.get('content')
            case = data.get('case')
            feedback = Feedback.objects.get(feedback_id = feedback_id)
            feedback.content = content
            feedback.save()
            serializer = FeedbackSerializer(feedback)
            return Response(serializer.data)
        
        elif(mode == 'delete'): # 피드백 삭제, feedback_id 필요
            feedback_id = data.get('feedback_id')
            feedback = Feedback.objects.get(feedback_id = feedback_id)
            feedback.delete()
            serializer = FeedbackSerializer(feedback)
            return Response(serializer.data)
        
        else:
            return Response("잘못된 요청입니다.")

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
    def get(self, request, format=None, type = None):
        rooms = Room.objects.filter(type = type)
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)

class RoomDetailView(APIView):
    def get(self, request, format=None, room_id = None):
        room = Room.objects.get(id = room_id)
        serializer = RoomSerializer(room)
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
                        # daytimetable.timetable[start:end+1] = '0' * (end - start)
                        reserve = '0' * (end - start)
                        daytimetable.timetable = daytimetable.timetable[:start] + reserve + daytimetable.timetable[end + 1:]
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
                    # daytimetable.timetable[start:end+1] = '0' * (end - start)
                    reserve = '0' * (end - start)
                    daytimetable.timetable = daytimetable.timetable[:start] + reserve + daytimetable.timetable[end + 1:]    
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