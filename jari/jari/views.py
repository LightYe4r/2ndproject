from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Users, Room, Reservation, Feedback, Post
from .serializer import UsersSerializer, RoomSerializer, ReservationSerializer, FeedbackSerializer, PostSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    
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
        user = Users.objects.create(name=name, student_id=student_id, password=password, status=status)
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
    
class RoomReservation(APIView):
    def post(self, request, format=None, *args, **kwargs):
        data = request.data
        room_id = data.get('room_id')
        user_id = data.get('user_id')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        reservation = Reservation.objects.create(room_id=room_id, user_id=user_id, start_time=start_time, end_time=end_time)
        reservation.save()
        room = Room.objects.get(id = room_id)
        room.status = True
        room.save()
        return Response({'message': '예약이 완료되었습니다.'})