from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class UserManager(BaseUserManager):
    def _create_user(self, username, kakao_id, **extra_fields):
        if not kakao_id:
            raise ValueError('카카오 로그인 정보가 없습니다.')
        user = self.model(
            username=username,
            # kakao_id=kakao_id, 
            **extra_fields
        )
        user.set_password(kakao_id)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, kakao_id, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(username, kakao_id, **extra_fields)
    
    def create_user(self, username, kakao_id, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, kakao_id, **extra_fields)
    
class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True)
    kakao_id = models.CharField(max_length=100, unique=True)
    REQUIRED_FIELDS = ['kakao_id']
    # USERNAME_FIELD = 'kakao_id'
    objects = UserManager()

class Room(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    start_hour = models.IntegerField()
    end_hour = models.IntegerField()
    type = models.CharField(max_length=100)
    people_num = models.IntegerField()
    status_choice = (
        ('on', '예약가능'),
        ('off', '예약불가능'),
    )
    status = models.CharField(max_length=100, choices=status_choice, default='on')
    
class DayTimeTable(models.Model):
    id = models.AutoField(primary_key=True)
    room_id = models.ForeignKey(Room, on_delete=models.CASCADE)
    date = models.DateField()
    timetable = models.CharField(max_length=48,default=[0]*48)

class Reservation(models.Model):
    id = models.AutoField(primary_key=True)
    room_id = models.ForeignKey(Room, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    start = models.DateTimeField()
    end = models.DateTimeField()
    create_at = models.DateTimeField(auto_now_add=True)
    people_num = models.IntegerField()
    date = models.DateField()
    extension = models.IntegerField(default=2)
    
class Feedback(models.Model):
    id = models.AutoField(primary_key=True)
    reservation_id = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    room_id = models.ForeignKey(Room, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    create_at = models.DateTimeField(auto_now_add=True)
    
class Post(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    status = models.CharField(max_length=100)
    create_at = models.DateTimeField(auto_now_add=True)