from django.contrib import admin
from .models import User, Room, Reservation, Feedback, Post

admin.site.register(User)
admin.site.register(Room)
admin.site.register(Reservation)
admin.site.register(Feedback)
admin.site.register(Post)