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
    objects = UserManager()

class Room(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100,unique=True)
    start_hour = models.IntegerField()
    end_hour = models.IntegerField()
    type = models.CharField(max_length=100)
    people_num = models.IntegerField()
    
class DayTimeTable(models.Model):
    id = models.AutoField(primary_key=True)
    room_id = models.ForeignKey(Room, on_delete=models.CASCADE)
    date = models.DateField()
    timetable = models.CharField(max_length=48,default='0'*48)

class Reservation(models.Model):
    id = models.AutoField(primary_key=True)
    room_id = models.ForeignKey(Room, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    start = models.IntegerField()
    end = models.IntegerField()
    create_at = models.DateTimeField(auto_now_add=True)
    people_num = models.IntegerField()
    date = models.DateField()
    extension = models.IntegerField(default=2)
    
class Feedback(models.Model):
    id = models.AutoField(primary_key=True)
    case = models.CharField(max_length=100)
    room_id = models.ForeignKey(Room, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=500)
    create_at = models.DateTimeField(auto_now_add=True)
    status_choice = (
        ('ready', '확인 전'),
        ('progress', '처리중'),
        ('done', '처리 완료'),
    )
    status = models.CharField(max_length=10, choices=status_choice, default='ready')
    
class Post(models.Model):
    post_id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    status = models.CharField(max_length=100)
    create_at = models.DateTimeField(auto_now_add=True)