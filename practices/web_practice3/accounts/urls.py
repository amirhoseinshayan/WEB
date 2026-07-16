from django.urls import path

from .views import (
    CustomTokenRefreshAPIView,
    LoginAPIView,
    ProfileAPIView,
    RegisterAPIView,
)


app_name = 'accounts'


urlpatterns = [
    path('auth/register/', RegisterAPIView.as_view(), name='register'),
    path('auth/login/', LoginAPIView.as_view(), name='login'),
    path('auth/token/refresh/', CustomTokenRefreshAPIView.as_view(), name='token-refresh'),
    path('auth/profile/', ProfileAPIView.as_view(), name='profile'),
]