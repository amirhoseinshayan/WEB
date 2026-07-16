from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.serializers import UserProfileSerializer

from .models import SubscriptionPlan
from .serializers import (
    PurchaseSubscriptionResponseSerializer,
    PurchaseSubscriptionSerializer,
    SubscriptionPlanSerializer,
    SubscriptionStatusSerializer,
)
from .services import (
    apply_subscription_plan_to_user,
    build_subscription_status,
)


class SubscriptionStatusAPIView(APIView):
    """
    Return current user's subscription status.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Subscription'],
        summary='Get current user subscription status',
        responses={
            200: SubscriptionStatusSerializer,
            401: OpenApiResponse(description='Authentication required.'),
        },
        examples=[
            OpenApiExample(
                name='Free User Status Response',
                value={
                    'subscription_type': 'free',
                    'plan_name': 'Free Plan',
                    'is_premium': False,
                    'premium_until': None,
                    'daily_message_limit': 50,
                    'daily_messages_used': 3,
                    'daily_messages_remaining': 47,
                    'can_use_premium_models': False,
                    'can_upload_files': False,
                },
                response_only=True,
                status_codes=['200'],
            ),
            OpenApiExample(
                name='Premium User Status Response',
                value={
                    'subscription_type': 'premium',
                    'plan_name': 'Premium Monthly',
                    'is_premium': True,
                    'premium_until': '2026-08-16T10:00:00Z',
                    'daily_message_limit': None,
                    'daily_messages_used': 15,
                    'daily_messages_remaining': None,
                    'can_use_premium_models': True,
                    'can_upload_files': True,
                },
                response_only=True,
                status_codes=['200'],
            ),
        ],
    )
    def get(self, request):
        status_data = build_subscription_status(request.user)

        return Response(status_data, status=status.HTTP_200_OK)


class SubscriptionPlanListAPIView(ListAPIView):
    """
    List active subscription plans.
    """

    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Subscription'],
        summary='List active subscription plans',
        responses={200: SubscriptionPlanSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return (
            SubscriptionPlan.objects
            .filter(is_active=True)
            .order_by('price', 'name')
        )


class PurchaseSubscriptionAPIView(APIView):
    """
    Simulate purchasing or switching to a subscription plan.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Subscription'],
        summary='Purchase or switch subscription plan',
        request=PurchaseSubscriptionSerializer,
        responses={
            200: PurchaseSubscriptionResponseSerializer,
            400: OpenApiResponse(description='Invalid plan selected.'),
            401: OpenApiResponse(description='Authentication required.'),
        },
        examples=[
            OpenApiExample(
                name='Purchase Premium Request',
                value={
                    'plan_id': 2,
                },
                request_only=True,
            ),
            OpenApiExample(
                name='Purchase Response',
                value={
                    'message': 'Subscription plan applied successfully.',
                    'plan': {
                        'id': 2,
                        'name': 'Premium Monthly',
                        'plan_type': 'premium',
                        'description': 'Monthly premium plan with access to premium models and file uploads.',
                        'price': '9.99',
                        'duration_days': 30,
                        'daily_message_limit': None,
                        'can_use_premium_models': True,
                        'can_upload_files': True,
                        'is_active': True,
                        'is_free': False,
                        'is_premium': True,
                        'created_at': '2026-01-01T10:00:00Z',
                        'updated_at': '2026-01-01T10:00:00Z',
                    },
                    'user': {
                        'id': 1,
                        'username': 'amir',
                        'email': 'amir@example.com',
                        'first_name': 'Amir',
                        'last_name': 'Shayan',
                        'subscription_type': 'premium',
                        'premium_until': '2026-08-16T10:00:00Z',
                        'is_premium': True,
                        'created_at': '2026-01-01T10:00:00Z',
                        'updated_at': '2026-01-01T10:00:00Z',
                    },
                    'subscription_status': {
                        'subscription_type': 'premium',
                        'plan_name': 'Premium Monthly',
                        'is_premium': True,
                        'premium_until': '2026-08-16T10:00:00Z',
                        'daily_message_limit': None,
                        'daily_messages_used': 0,
                        'daily_messages_remaining': None,
                        'can_use_premium_models': True,
                        'can_upload_files': True,
                    },
                },
                response_only=True,
                status_codes=['200'],
            ),
        ],
    )
    def post(self, request):
        serializer = PurchaseSubscriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        plan = serializer.validated_data['plan']

        apply_subscription_plan_to_user(request.user, plan)

        request.user.refresh_from_db()

        return Response(
            {
                'message': 'Subscription plan applied successfully.',
                'plan': SubscriptionPlanSerializer(plan).data,
                'user': UserProfileSerializer(request.user).data,
                'subscription_status': build_subscription_status(request.user),
            },
            status=status.HTTP_200_OK,
        )