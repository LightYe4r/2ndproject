from django.contrib import admin
from .models import Users, Room, Reservation, Feedback, Post

admin.site.register(Users)
admin.site.register(Room)
admin.site.register(Reservation)
admin.site.register(Feedback)
admin.site.register(Post)