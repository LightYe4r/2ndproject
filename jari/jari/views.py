from django.shortcuts import render, redirect
from django.conf import settings
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, Room, Reservation, Feedback, Post, DayTimeTable
from .serializer import UserSerializer, RoomSerializer, ReservationSerializer, FeedbackSerializer, PostSerializer
from django.http import JsonResponse
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from json.decoder import JSONDecodeError
from rest_framework import status
import requests
import urllib

BASE_URL = 'https://port-0-toy-k19y2kljwq5eju.sel4.cloudtype.app/'
KAKAO_CALLBACK_URI = BASE_URL + 'kakao/callback/'
client_id = getattr(settings, 'SOCIAL_AUTH_KAKAO_KEY')
def kakao_login(request):
    return redirect(
        f'https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={KAKAO_CALLBACK_URI}&response_type=code&scope=account_email'
    )

def kakao_callback(request):
    code = request.GET.get('code')
    
    token_request = requests.post(f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={client_id}&redirect_uri={KAKAO_CALLBACK_URI}&code={code}")
    token_response_json = token_request.json()
    
    error = token_response_json.get('error', None)
    if error is not None:
        raise JSONDecodeError(error)
    access_token = token_response_json.get('access_token')
    
    profile_request = requests.get(
        "https://kapi.kakao.com/v2/user/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    profile_json = profile_request.json()
    kakao_account = profile_json.get('kakao_account')
    email = kakao_account.get('email', None)
    try:
        user = User.objects.get(email=email)
        token = TokenObtainPairSerializer.get_token(user)
        return Response({'refresh_token': str(token), 'token': str(token.access_token)})
    except User.DoesNotExist:
        user = User.objects.create_user(
            email=email
        )
        user.save()
        token = TokenObtainPairSerializer.get_token(user)
        return Response({'refresh_token': str(token), 'token': str(token.access_token)})

    
class KakaoLogin(SocialLoginView):
    adapter_class = KakaoOAuth2Adapter
    client_class = OAuth2Client
    callback_url = KAKAO_CALLBACK_URI
    
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
    
class CreateAccount(APIView):
    def post(self, request, format=None, *args, **kwargs):
        data = request.data
        name = data.get('name')
        student_id = data.get('student_id')
        password = data.get('password')
        status = data.get('status')
        user = User.objects.create(name=name, student_id=student_id, password=password, status=status)
        user.save()
        return Response({'message': '회원가입이 완료되었습니다.'})
    
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
    
# class RoomReservation(APIView):
#     def post(self, request, format=None, *args, **kwargs):
#         data = request.data
#         room_id = data.get('room_id')
#         user_id = data.get('user_id')
#         start_time = data.get('start_time')
#         end_time = data.get('end_time')
#         reservation = Reservation.objects.create(room_id=room_id, user_id=user_id, start_time=start_time, end_time=end_time)
#         reservation.save()
#         room = Room.objects.get(id = room_id)
#         room.status = True
#         room.save()
#         return Response({'message': '예약이 완료되었습니다.'})

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