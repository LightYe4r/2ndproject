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
from django.http import JsonResponse
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from json.decoder import JSONDecodeError
from rest_framework import status
from datetime import datetime
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
# 날짜와 타입을 받아서 해당하는 날짜와 타입의 가능한 방의 개수를 반환하고 처음 조회된다면 생성
class SearchDayTable(APIView):
    def get(self, request, format=None, date = None, type = None):
        Rooms = Room.objects.filter(type = type)
        room_num = Rooms.count()
        table = [room_num]*26
        for room in Rooms:
            try:
                daytimetable = DayTimeTable.objects.get(room_id = room, date = date)
                for i in range(26):
                    if(daytimetable.timetable[i] != '0'):
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

#날짜,방,그리고 시간을 받아서 가능한 방들의 정보를 반환
class SearchDayTimeTable(APIView): 
    def get(self, request, format=None, date = None, type = None, start = None, end = None):
        Rooms = Room.objects.filter(type = type)
        for room in Rooms:
            daytimetable = DayTimeTable.objects.get(room_id = room, date = date)
            if('1' in daytimetable.timetable[start:end+1] or '2' in daytimetable.timetable[start:end+1]):
                Rooms = Rooms.exclude(id = room.id)
        serializer = RoomSerializer(Rooms, many=True)
        return Response(serializer.data)

# 날짜에 해당하는 모든 방의 시간표를 반환
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
# 방과 날짜를 받아서 해당하는 방의 날짜의 시간표를 반환
class SearchRoomTimeTable(APIView):
    def get(self, request, format=None, room_name = None, date = None):
        room = Room.objects.get(name = room_name)
        daytimetable = DayTimeTable.objects.get(room_id = room, date = date)
        serializer = DayTimeTableSerializer(daytimetable)
        return Response(serializer.data)
    
"""request
{
    "room_name" : "smash0",
    "date" : "2023-11-13",
    "kakao_id" : "jihoon",
    "start" : 0,
    "end" : 1,
    "people_num" : 2,
    "current_date" : "2023-11-12",
    "current_index" : 10
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
        current_date = data.get('current_date')
        current_index = data.get('current_index')
        room = Room.objects.get(name=room_name)
        user = User.objects.get(kakao_id=kakao_id)

        reservations = Reservation.objects.filter(user_id=user).order_by('id').last()

        if reservations:
            date_format = '%Y-%m-%d'
            reserved_date = datetime.strptime(str(reservations.date), date_format)
            current_date = datetime.strptime(str(current_date), date_format)
            diff = reserved_date - current_date

            if diff.days > 0:
                return JsonResponse({"error": "앞선 예약이 있습니다."})
            elif diff.days == 0 and reservations.end >= current_index:
                return JsonResponse({"error": "이용 중이거나 예약된 내역이 있습니다."})
            elif diff.days == 0 and reservations.end < current_index:
                daytimetable = DayTimeTable.objects.get(room_id=room, date=date)
                if '1' not in daytimetable.timetable[start:end + 1] and '2' not in daytimetable.timetable[start:end + 1]:
                    reserve = '1' * (end - start + 1)
                    daytimetable.timetable = daytimetable.timetable[:start] + reserve + daytimetable.timetable[end + 1:]
                    reservation = Reservation.objects.create(room_id=room, date=date, user_id=user, start=start, end=end, people_num=people_num)
                    reservation.save()
                    serializer = ReservationSerializer(reservation)
                    daytimetable.save()
                    return Response(serializer.data)
                else:
                    serializer = DayTimeTableSerializer(daytimetable)
                    return JsonResponse({"error": "다른 예약이 있습니다."})
            else:
                daytimetable = DayTimeTable.objects.get(room_id=room, date=date)
                if '1' not in daytimetable.timetable[start:end + 1] and '2' not in daytimetable.timetable[start:end + 1]:
                    reserve = '1' * (end - start + 1)
                    daytimetable.timetable = daytimetable.timetable[:start] + reserve + daytimetable.timetable[end + 1:]
                    reservation = Reservation.objects.create(room_id=room, date=date, user_id=user, start=start, end=end, people_num=people_num)
                    reservation.save()
                    serializer = ReservationSerializer(reservation)
                    daytimetable.save()
                    return Response(serializer.data)
                else:
                    serializer = DayTimeTableSerializer(daytimetable)
                    return JsonResponse({"error": "다른 예약이 있습니다."})
        else:
            daytimetable = DayTimeTable.objects.get(room_id=room, date=date)
            if '1' not in daytimetable.timetable[start:end + 1] and '2' not in daytimetable.timetable[start:end + 1]:
                reserve = '1' * (end - start + 1)
                daytimetable.timetable = daytimetable.timetable[:start] + reserve + daytimetable.timetable[end + 1:]
                reservation = Reservation.objects.create(room_id=room, date=date, user_id=user, start=start, end=end, people_num=people_num)
                reservation.save()
                serializer = ReservationSerializer(reservation)
                daytimetable.save()
                return Response(serializer.data)
            else:
                serializer = DayTimeTableSerializer(daytimetable)
                return JsonResponse({"error": "다른 예약이 있습니다."})

            
"""request
{
    "kakao_id" : 1
}
"""

class ReservationList(APIView):
    def post(self, request, format=None):
        data = request.data
        kakao_id = data.get('kakao_id')
        user = User.objects.get(kakao_id = kakao_id)
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
        reservation = Reservation.objects.filter(room_id = room, date = date, user_id = user).order_by('id').last()
        if reservation:
            start = reservation.start
            end = reservation.end
            daytimetable = DayTimeTable.objects.get(room_id = room, date = date)
            reserve = '0' * (end - start +1 )
            daytimetable.timetable = daytimetable.timetable[:start] + reserve + daytimetable.timetable[end + 1:]
            daytimetable.save()
            reservation.delete()
            serializer = DayTimeTableSerializer(daytimetable)
            return Response(serializer.data)
        else:
            return JsonResponse({"error": "해당 예약이 없습니다."})
    
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
        current_index = data.get('current_index')
        current_date = data.get('current_date')
        room = Room.objects.get(name = room_name)
        user = User.objects.get(kakao_id = kakao_id)
        reservation = Reservation.objects.filter(room_id = room, date = date, user_id = user).order_by('id').last()
        extension = reservation.extension
        date_format = '%Y-%m-%d'
        reserved_date = datetime.strptime(str(reservation.date), date_format)
        current_date = datetime.strptime(str(current_date), date_format)
        diff = reserved_date - current_date
        if(diff.days == 0):
            if(end == current_index):
                if(extension > 0 ):
                    end = reservation.end
                    daytimetable = DayTimeTable.objects.get(room_id = room, date = date)
                    if('1' not in daytimetable.timetable[end+1:end+2] and '2' not in daytimetable.timetable[end+1:end+2]):
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
                    return Response({"error": "연장 횟수를 다 썼습니다."})
            else:
                return Response({"error": "아직 연장할 수 없습니다."})
        else:
            return Response({"error": "예약 날짜가 아직 아닙니다"})
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
    "kakao_id" : "jihoon",
    "current_date" : "2023-10-12",
    "current_index" : 10
}"""

class SearchMyReservation(APIView):
    def post(self, request, format=None):
        data = request.data
        kakao_id = data.get('kakao_id')
        current_date = data.get('current_date')
        current_index = data.get('current_index')
        user = User.objects.get(kakao_id=kakao_id)

        reservations = Reservation.objects.filter(user_id=user).order_by('id')

        if reservations.exists():
            reservation = reservations.last()
            date_format = '%Y-%m-%d'
            reserved_date = datetime.strptime(str(reservation.date), date_format)
            current_date = datetime.strptime(str(current_date), date_format)
            diff = reserved_date - current_date

            if diff.days <= 0:
                if diff.days == 0 and reservation.end < current_index:
                    return JsonResponse({"error": "이용 중이거나 예약된 내역이 없습니다."})
                elif diff.days == 0 and reservation.end >= current_index:
                    room = reservation.room_id
                    daytimetable = DayTimeTable.objects.filter(date=reservation.date, room_id=room)
                    serializer = MyPageSerializer({"reservations": reservation, "daytimetable": daytimetable})
                    return Response(serializer.data)
                else:
                    return JsonResponse({"error": "예약이 없습니다."})
                    
            else:
                room = reservation.room_id
                daytimetable = DayTimeTable.objects.filter(date=reservation.date, room_id=room)
                serializer = MyPageSerializer({"reservations": reservation, "daytimetable": daytimetable})
                return Response(serializer.data)
        else:
            return JsonResponse({"error": "예약이 없습니다."})


    
"""request
{
    "room_name" : "smash0",
    "kakao_id" : "1234",
    "content" : "test"
}"""
    
class CreateFeedback(APIView):
    def post(self, request, format=None):
        data = request.data
        room_name = data.get('room_name')
        kakao_id = data.get('kakao_id')
        case = data.get('case')
        content = data.get('content')
        room = Room.objects.get(name = room_name)
        user = User.objects.get(kakao_id = kakao_id)
        feedback = Feedback.objects.create(room_id = room, user_id = user, case = case, content = content)
        feedback.save()
        serializer = FeedbackSerializer(feedback)
        return Response(serializer.data)

class ReadFeedback(APIView):
    def post(self, request, format=None):
        data = request.data
        feedback_id = data.get('feedback_id')
        room_name = data.get('room_name')
        kakao_id = data.get('kakao_id')
        case = data.get('case')
        status = data.get('status')
        if(feedback_id):
            feedback = Feedback.objects.get(id = feedback_id)
            serializer = FeedbackSerializer(feedback)
            
        elif(kakao_id):
            user = User.objects.get(kakao_id = kakao_id)
            feedbacks = Feedback.objects.filter(user_id = user)
            serializer = FeedbackSerializer(feedbacks, many=True)
            
        elif(case):
            feedbacks = Feedback.objects.filter(case = case)
            serializer = FeedbackSerializer(feedbacks, many=True)
            
        elif(status):
            feedbacks = Feedback.objects.filter(status = status)
            serializer = FeedbackSerializer(feedbacks, many=True)
            
        elif(room_name):
            room = Room.objects.get(name = room_name)
            feedbacks = Feedback.objects.filter(room_id = room)
            serializer = FeedbackSerializer(feedbacks, many=True)
            
        else:
            feedbacks = Feedback.objects.all()
            serializer = FeedbackSerializer(feedbacks, many=True)
            
        return Response(serializer.data)

class UpdateFeedback(APIView):
    def post(self, request, format=None):
        data = request.data
        feedback_id = data.get('feedback_id')
        kakao_id = data.get('kakao_id')
        case = data.get('case')
        status = data.get('status')
        content = data.get('content')
        feedback = Feedback.objects.get(id = feedback_id)
        feedback.status = status
        feedback.content = content
        feedback.case = case
        feedback.save()
        serializer = FeedbackSerializer(feedback)
        return Response(serializer.data)
    
class DeleteFeedback(APIView):
    def post(self, request, format=None):
        data = request.data
        feedback_id = data.get('feedback_id')
        feedback = Feedback.objects.get(id = feedback_id)
        feedback.delete()
        return Response("Delete Success")
    
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
        room_name = data.get('room_name')
        date = data.get('date')
        start = data.get('start')
        end = data.get('end')
        command = data.get('command')
        if(room_name == 'all'):
            rooms = Room.objects.all()
            if(command == 'on'):
                for room in rooms:
                    daytimetable = DayTimeTable.objects.get(room_id = room, date = date)
                    if daytimetable:
                        if('1' not in daytimetable.timetable[start:end+1]):
                            reserve = '0' * (end - start +1)
                            daytimetable.timetable = daytimetable.timetable[:start] + reserve + daytimetable.timetable[end + 1:]
                            daytimetable.save()
                    else:
                        serializer = DayTimeTableSerializer(daytimetable)
                        return Response(serializer.data)
            elif(command == 'off'):
                for room in rooms:
                    daytimetable = DayTimeTable.objects.get(room_id = room, date = date)
                    if daytimetable:
                        if('1' not in daytimetable.timetable[start:end+1]):
                            reserve = '2' * (end - start +1)
                            daytimetable.timetable = daytimetable.timetable[:start] + reserve + daytimetable.timetable[end + 1:]
                            daytimetable.save()
                        else:
                            serializer = DayTimeTableSerializer(daytimetable)
                            return Response(serializer.data)
                    else:
                        pass
            serializer = RoomSerializer(rooms, many=True)
            return Response(serializer.data)
        else:
            room = Room.objects.get(name = room_name)
            if(command == 'on'):
                daytimetable = DayTimeTable.objects.get(room_id = room, date = date)
                if daytimetable:
                    if('1' not in daytimetable.timetable[start:end+1]):
                        reserve = '0' * (end - start +1)
                        daytimetable.timetable = daytimetable.timetable[:start] + reserve + daytimetable.timetable[end + 1:]
                        daytimetable.save()
                else:
                    serializer = DayTimeTableSerializer(daytimetable)
                    return Response(serializer.data)
            elif(command == 'off'):
                daytimetable = DayTimeTable.objects.get(room_id = room, date = date)
                if daytimetable:
                    if('1' not in daytimetable.timetable[start:end+1]):
                        reserve = '2' * (end - start +1)
                        daytimetable.timetable = daytimetable.timetable[:start] + reserve + daytimetable.timetable[end + 1:]
                        daytimetable.save()
                    else:
                        serializer = DayTimeTableSerializer(daytimetable)
                        return Response(serializer.data)
                else:
                    pass
            serializer = RoomSerializer(room)
            return Response(serializer.data) 
        
class RequestUserId(APIView):
    def post(self, request, format=None):
        data = request.data
        kakao_id = data.get('kakao_id')
        try:
            user = User.objects.get(kakao_id = kakao_id)
            return Response(user.id)
        except User.DoesNotExist:
            return Response("user does not exist")