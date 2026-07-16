from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveDestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .models import LinkedAccount
from .serializers import (
    LinkedAccountCreateResponseSerializer,
    LinkedAccountCreateSerializer,
    LinkedAccountSerializer,
    LoginResponseSerializer,
    LoginSerializer,
    ProfileResponseSerializer,
    RegisterResponseSerializer,
    RegisterSerializer,
    SwitchAccountResponseSerializer,
    SwitchAccountSerializer,
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
            )
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
            )
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
            )
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


class LinkedAccountListCreateAPIView(ListCreateAPIView):
    """
    List and create linked account relations for the current user.
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            LinkedAccount.objects
            .select_related('owner', 'linked_user')
            .filter(owner=self.request.user)
            .order_by('-created_at')
        )

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return LinkedAccountCreateSerializer

        return LinkedAccountSerializer

    @extend_schema(
        tags=['Linked Accounts'],
        summary='List current user linked accounts',
        responses={
            200: LinkedAccountSerializer(many=True),
            401: OpenApiResponse(description='Authentication required.'),
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=['Linked Accounts'],
        summary='Link another account by username or email',
        request=LinkedAccountCreateSerializer,
        responses={
            201: OpenApiResponse(
                response=LinkedAccountCreateResponseSerializer,
                description='Account linked successfully.',
            ),
            400: OpenApiResponse(description='Invalid linked account data.'),
            401: OpenApiResponse(description='Authentication required.'),
        },
        examples=[
            OpenApiExample(
                name='Link Account Request',
                value={
                    'identifier': 'second_user@example.com',
                },
                request_only=True,
            )
        ],
    )
    def post(self, request, *args, **kwargs):
        serializer = LinkedAccountCreateSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)

        linked_account = serializer.save()

        return Response(
            {
                'message': 'Account linked successfully.',
                'linked_account': LinkedAccountSerializer(linked_account).data,
            },
            status=status.HTTP_201_CREATED,
        )


class LinkedAccountDetailAPIView(RetrieveDestroyAPIView):
    """
    Retrieve or delete a linked account relation owned by current user.
    """

    serializer_class = LinkedAccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            LinkedAccount.objects
            .select_related('owner', 'linked_user')
            .filter(owner=self.request.user)
        )

    @extend_schema(
        tags=['Linked Accounts'],
        summary='Retrieve a linked account',
        responses={
            200: LinkedAccountSerializer,
            404: OpenApiResponse(description='Linked account not found.'),
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=['Linked Accounts'],
        summary='Delete a linked account relation',
        responses={
            204: OpenApiResponse(description='Linked account deleted successfully.'),
            404: OpenApiResponse(description='Linked account not found.'),
        },
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class SwitchAccountAPIView(APIView):
    """
    Switch to an active linked account and receive JWT tokens for that account.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Linked Accounts'],
        summary='Switch to a linked account',
        request=SwitchAccountSerializer,
        responses={
            200: OpenApiResponse(
                response=SwitchAccountResponseSerializer,
                description='Switched account successfully.',
            ),
            400: OpenApiResponse(description='Account is not linked or inactive.'),
            401: OpenApiResponse(description='Authentication required.'),
        },
        examples=[
            OpenApiExample(
                name='Switch Account Request',
                value={
                    'linked_user_id': 2,
                },
                request_only=True,
            )
        ],
    )
    def post(self, request):
        serializer = SwitchAccountSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)

        switched_from = request.user
        switched_to = serializer.linked_user

        refresh = RefreshToken.for_user(switched_to)

        return Response(
            {
                'message': 'Switched account successfully.',
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'switched_from': UserProfileSerializer(switched_from).data,
                'switched_to': UserProfileSerializer(switched_to).data,
            },
            status=status.HTTP_200_OK,
        )