from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Users, Room, Reservation, Feedback, Post, DayTimeTable
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