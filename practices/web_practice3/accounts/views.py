from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView

from .serializers import (
    LoginResponseSerializer,
    LoginSerializer,
    ProfileResponseSerializer,
    RegisterResponseSerializer,
    RegisterSerializer,
    TokenRefreshRequestSerializer,
    TokenRefreshResponseSerializer,
    UserProfileSerializer,
)


class RegisterAPIView(APIView):
    """
    Register a new user account.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Authentication'],
        auth=[],
        request=RegisterSerializer,
        responses={
            201: OpenApiResponse(
                response=RegisterResponseSerializer,
                description='User registered successfully.',
            ),
            400: OpenApiResponse(description='Invalid registration data.'),
        },
        examples=[
            OpenApiExample(
                name='Register Request',
                value={
                    'username': 'amir',
                    'email': 'amir@example.com',
                    'first_name': 'Amir',
                    'last_name': 'Shayan',
                    'password': 'StrongPass123!',
                    'password_confirm': 'StrongPass123!',
                },
                request_only=True,
            ),
            OpenApiExample(
                name='Register Response',
                value={
                    'message': 'User registered successfully.',
                    'user': {
                        'id': 1,
                        'username': 'amir',
                        'email': 'amir@example.com',
                        'first_name': 'Amir',
                        'last_name': 'Shayan',
                        'subscription_type': 'free',
                        'premium_until': None,
                        'is_premium': False,
                        'created_at': '2026-01-01T10:00:00Z',
                        'updated_at': '2026-01-01T10:00:00Z',
                    },
                },
                response_only=True,
                status_codes=['201'],
            ),
        ],
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        user_data = UserProfileSerializer(user).data

        return Response(
            {
                'message': 'User registered successfully.',
                'user': user_data,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginAPIView(APIView):
    """
    Login with username or email and receive JWT tokens.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Authentication'],
        auth=[],
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(
                response=LoginResponseSerializer,
                description='Login successful.',
            ),
            400: OpenApiResponse(description='Invalid credentials.'),
        },
        examples=[
            OpenApiExample(
                name='Login With Username',
                value={
                    'identifier': 'amir',
                    'password': 'StrongPass123!',
                },
                request_only=True,
            ),
            OpenApiExample(
                name='Login With Email',
                value={
                    'identifier': 'amir@example.com',
                    'password': 'StrongPass123!',
                },
                request_only=True,
            ),
            OpenApiExample(
                name='Login Response',
                value={
                    'message': 'Login successful.',
                    'access': 'jwt-access-token',
                    'refresh': 'jwt-refresh-token',
                    'user': {
                        'id': 1,
                        'username': 'amir',
                        'email': 'amir@example.com',
                        'first_name': 'Amir',
                        'last_name': 'Shayan',
                        'subscription_type': 'free',
                        'premium_until': None,
                        'is_premium': False,
                        'created_at': '2026-01-01T10:00:00Z',
                        'updated_at': '2026-01-01T10:00:00Z',
                    },
                },
                response_only=True,
                status_codes=['200'],
            ),
        ],
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        user = validated_data['user']

        return Response(
            {
                'message': 'Login successful.',
                'access': validated_data['access'],
                'refresh': validated_data['refresh'],
                'user': UserProfileSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class CustomTokenRefreshAPIView(TokenRefreshView):
    """
    Refresh JWT access token using a valid refresh token.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Authentication'],
        auth=[],
        request=TokenRefreshRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=TokenRefreshResponseSerializer,
                description='Access token refreshed successfully.',
            ),
            401: OpenApiResponse(description='Refresh token is invalid or expired.'),
        },
        examples=[
            OpenApiExample(
                name='Token Refresh Request',
                value={
                    'refresh': 'jwt-refresh-token',
                },
                request_only=True,
            ),
            OpenApiExample(
                name='Token Refresh Response',
                value={
                    'access': 'new-jwt-access-token',
                },
                response_only=True,
                status_codes=['200'],
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ProfileAPIView(APIView):
    """
    Retrieve or update the authenticated user's profile.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Authentication'],
        responses={
            200: OpenApiResponse(
                response=ProfileResponseSerializer,
                description='Profile retrieved successfully.',
            ),
            401: OpenApiResponse(description='Authentication credentials were not provided or are invalid.'),
        },
        examples=[
            OpenApiExample(
                name='Profile Response',
                value={
                    'message': 'Profile retrieved successfully.',
                    'user': {
                        'id': 1,
                        'username': 'amir',
                        'email': 'amir@example.com',
                        'first_name': 'Amir',
                        'last_name': 'Shayan',
                        'subscription_type': 'free',
                        'premium_until': None,
                        'is_premium': False,
                        'created_at': '2026-01-01T10:00:00Z',
                        'updated_at': '2026-01-01T10:00:00Z',
                    },
                },
                response_only=True,
                status_codes=['200'],
            ),
        ],
    )
    def get(self, request):
        user_data = UserProfileSerializer(request.user).data

        return Response(
            {
                'message': 'Profile retrieved successfully.',
                'user': user_data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=['Authentication'],
        request=UserProfileSerializer,
        responses={
            200: OpenApiResponse(
                response=ProfileResponseSerializer,
                description='Profile updated successfully.',
            ),
            400: OpenApiResponse(description='Invalid profile data.'),
            401: OpenApiResponse(description='Authentication credentials were not provided or are invalid.'),
        },
        examples=[
            OpenApiExample(
                name='Profile Update Request',
                value={
                    'first_name': 'Amirhosein',
                    'last_name': 'Shayan',
                    'email': 'amirhosein@example.com',
                },
                request_only=True,
            ),
            OpenApiExample(
                name='Profile Update Response',
                value={
                    'message': 'Profile updated successfully.',
                    'user': {
                        'id': 1,
                        'username': 'amir',
                        'email': 'amirhosein@example.com',
                        'first_name': 'Amirhosein',
                        'last_name': 'Shayan',
                        'subscription_type': 'free',
                        'premium_until': None,
                        'is_premium': False,
                        'created_at': '2026-01-01T10:00:00Z',
                        'updated_at': '2026-01-01T10:05:00Z',
                    },
                },
                response_only=True,
                status_codes=['200'],
            ),
        ],
    )
    def patch(self, request):
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                'message': 'Profile updated successfully.',
                'user': serializer.data,
            },
            status=status.HTTP_200_OK,
        )