from django.contrib import admin
from django.urls import path, include
from .views import UserViewSet, PostViewSet, RoomViewSet, ReservationViewSet, FeedbackViewSet, CreateAccount, RoomList, RoomDetailView, RoomReservation, kakao_login, kakao_callback, KakaoLogin
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
    path('kakao/login/', kakao_login, name='kakao_login'),
    path('kakao/callback/', kakao_callback, name='kakao_callback'),
    path('kakao/login/finish/', KakaoLogin.as_view(), name='kakao_login_finish'),
]
