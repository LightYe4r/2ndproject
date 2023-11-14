import rest_framework.serializers as serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        
class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'
        
class ReservationSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(source='room_id.name', read_only=True)
    class Meta:
        model = Reservation
        fields = '__all__'
        
class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'
        
class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

class DayTimeTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = DayTimeTable
        fields = '__all__'

class MyPageSerializer(serializers.Serializer):
    reservations = ReservationSerializer(many=False)
    daytimetable = DayTimeTableSerializer(many=True)