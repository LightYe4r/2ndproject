from django.contrib import admin
from django.urls import path, include
from .views import UserViewSet, PostViewSet, RoomViewSet, ReservationViewSet, FeedbackViewSet
from rest_framework import routers

routers = routers.DefaultRouter()
routers.register('users', UserViewSet)
routers.register('posts', PostViewSet)
routers.register('rooms', RoomViewSet)
routers.register('reservations', ReservationViewSet)
routers.register('feedbacks', FeedbackViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(routers.urls)),
]
