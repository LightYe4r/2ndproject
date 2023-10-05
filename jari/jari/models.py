from django.db import models

class Users(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    create_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100)
    
class Room(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    start_hour = models.IntegerField()
    end_hour = models.IntegerField()
    location = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    
class Reservation(models.Model):
    id = models.AutoField(primary_key=True)
    room_id = models.ForeignKey(Room, on_delete=models.CASCADE)
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    create_at = models.DateTimeField(auto_now_add=True)
    people_num = models.IntegerField()
    status = models.CharField(max_length=100)
    
class Feedback(models.Model):
    id = models.AutoField(primary_key=True)
    reservation_id = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    room_id = models.ForeignKey(Room, on_delete=models.CASCADE)
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    content = models.TextField()
    create_at = models.DateTimeField(auto_now_add=True)
    
class Post(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    content = models.TextField()
    create_at = models.DateTimeField(auto_now_add=True)