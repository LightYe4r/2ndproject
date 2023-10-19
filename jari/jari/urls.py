from django.contrib import admin
from django.urls import path, include
from .views import UserViewSet, PostViewSet, RoomViewSet, ReservationViewSet, FeedbackViewSet, RoomList, RoomDetailView, RoomReservation, Login, SearchDayTimeTable, RoomControl
from rest_framework import routers
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

routers = routers.DefaultRouter()
routers.register('users', UserViewSet)
routers.register('posts', PostViewSet)
routers.register('rooms', RoomViewSet)
routers.register('reservations', ReservationViewSet)
routers.register('feedbacks', FeedbackViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(routers.urls)),
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    path('login/', Login.as_view()),
    path('roomreserve/', RoomReservation.as_view()),
    path('searchtimetable/',SearchDayTimeTable.as_view()),
    path('control/',RoomControl.as_view()),
]
