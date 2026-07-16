from django.urls import path

from .views import (
    PurchaseSubscriptionAPIView,
    SubscriptionPlanListAPIView,
    SubscriptionStatusAPIView,
)


app_name = 'subscriptions'


urlpatterns = [
    path(
        'subscription/status/',
        SubscriptionStatusAPIView.as_view(),
        name='subscription-status',
    ),
    path(
        'subscription/plans/',
        SubscriptionPlanListAPIView.as_view(),
        name='subscription-plans',
    ),
    path(
        'subscription/purchase/',
        PurchaseSubscriptionAPIView.as_view(),
        name='subscription-purchase',
    ),
]