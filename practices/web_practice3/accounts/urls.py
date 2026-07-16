from django.urls import path

from .views import (
    CustomTokenRefreshAPIView,
    LinkedAccountDetailAPIView,
    LinkedAccountListCreateAPIView,
    LoginAPIView,
    ProfileAPIView,
    RegisterAPIView,
    SwitchAccountAPIView,
)


app_name = 'accounts'


urlpatterns = [
    path('auth/register/', RegisterAPIView.as_view(), name='register'),
    path('auth/login/', LoginAPIView.as_view(), name='login'),
    path('auth/token/refresh/', CustomTokenRefreshAPIView.as_view(), name='token-refresh'),
    path('auth/profile/', ProfileAPIView.as_view(), name='profile'),
    path('auth/switch-account/', SwitchAccountAPIView.as_view(), name='switch-account'),

    path('linked-accounts/', LinkedAccountListCreateAPIView.as_view(), name='linked-account-list-create'),
    path('linked-accounts/<int:pk>/', LinkedAccountDetailAPIView.as_view(), name='linked-account-detail'),
]