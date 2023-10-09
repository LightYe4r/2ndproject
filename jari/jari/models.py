from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, **extra_fields):
        if not email:
            raise ValueError('이메일은 필수입니다.')
        user = self.model(
            email=email, 
            **extra_fields
        )
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password, **extra_fields):
        superuser = self.create_user(
            email=email,  
        )
        superuser.is_staff = True
        superuser.is_superuser = True
        superuser.is_activate = True
        superuser.save(using=self._db)
        return superuser
    
class User(AbstractUser):
    email = models.EmailField(max_length=100, unique=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_activate = models.BooleanField(default=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [email]
    objects = UserManager()

class Room(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    date = models.DateField()
    start_hour = models.IntegerField()
    end_hour = models.IntegerField()
    timetable = [0] * 24
    type = models.CharField(max_length=100)
    people_num = models.IntegerField()
    status = models.CharField(max_length=100)
    
class DayTimeTable(models.Model):
    id = models.AutoField(primary_key=True)
    room_id = models.ForeignKey(Room, on_delete=models.CASCADE)
    day = models.DateField()
    timetable = models.CharField(max_length=48,default="0"*48)

class Reservation(models.Model):
    id = models.AutoField(primary_key=True)
    room_id = models.ForeignKey(Room, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    create_at = models.DateTimeField(auto_now_add=True)
    people_num = models.IntegerField()
    status = models.CharField(max_length=100)
    
class Feedback(models.Model):
    id = models.AutoField(primary_key=True)
    reservation_id = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    room_id = models.ForeignKey(Room, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    create_at = models.DateTimeField(auto_now_add=True)
    
class Post(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    content = models.TextField()
    create_at = models.DateTimeField(auto_now_add=True)