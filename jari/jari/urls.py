from django.contrib import admin
from django.urls import path, include
from .views import *
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
    # path('dj-rest-auth/', include('dj_rest_auth.urls')),
    # path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    path('login/', Login.as_view()),
    path('roomreserve/', RoomReservation.as_view()),
    path('searchtimetable/<str:date>/<str:type>/<int:start>/<int:end>/',SearchDayTimeTable.as_view()),
    path('searchdaytable/<str:date>/<str:type>/',SearchDayTable.as_view()),
    path('searchdaytimetables/<str:date>/',SearchDayTimeTables.as_view()),
    path('searchroomtable/<int:room_id>/<str:date>/',SearchRoomTimeTable.as_view()),
    path('searchmyreservation/',SearchMyReservation.as_view()),
    path('reservationlist/',ReservationList.as_view()),
    path('deletereservation/',DeleteReservation.as_view()),
    path('extendreservation/',ExtendReservation.as_view()),
    path('control/',RoomControl.as_view()),
    path('refresh-token/', RefreshTokenView.as_view()),
    path('createfeedback/', CreateFeedback.as_view()),
    path('readfeedback/', ReadFeedback.as_view()),
    path('updatefeedback/', UpdateFeedback.as_view()),
    path('deletefeedback/', DeleteFeedback.as_view()),
    path('requestuserID/', RequestUserId.as_view()),
]