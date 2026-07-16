from django.contrib.auth import authenticate, get_user_model
from django.db.models import Q
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for reading and updating the authenticated user's profile.

    Subscription fields are read-only here because subscription upgrades
    will be handled through the subscription purchase API in later phases.
    """

    is_premium = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'subscription_type',
            'premium_until',
            'is_premium',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'subscription_type',
            'premium_until',
            'is_premium',
            'created_at',
            'updated_at',
        )

    def validate_username(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError('Username cannot be empty.')

        user = self.instance
        queryset = User.objects.filter(username__iexact=value)

        if user is not None:
            queryset = queryset.exclude(pk=user.pk)

        if queryset.exists():
            raise serializers.ValidationError('A user with this username already exists.')

        return value

    def validate_email(self, value):
        value = value.strip().lower()

        if not value:
            raise serializers.ValidationError('Email cannot be empty.')

        user = self.instance
        queryset = User.objects.filter(email__iexact=value)

        if user is not None:
            queryset = queryset.exclude(pk=user.pk)

        if queryset.exists():
            raise serializers.ValidationError('A user with this email already exists.')

        return value


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for registering a new user.
    """

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'},
    )

    password_confirm = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'},
    )

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
            'password_confirm',
        )
        read_only_fields = ('id',)

    def validate_username(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError('Username cannot be empty.')

        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError('A user with this username already exists.')

        return value

    def validate_email(self, value):
        value = value.strip().lower()

        if not value:
            raise serializers.ValidationError('Email cannot be empty.')

        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')

        return value

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')

        if password != password_confirm:
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match.'
            })

        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')

        password = validated_data.pop('password')
        email = validated_data.get('email', '').lower()

        user = User.objects.create_user(
            username=validated_data.get('username'),
            email=email,
            password=password,
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )

        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for logging in with username or email.

    The client can send one of these:
    - identifier
    - username
    - email
    """

    identifier = serializers.CharField(required=False, write_only=True)
    username = serializers.CharField(required=False, write_only=True)
    email = serializers.EmailField(required=False, write_only=True)

    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
    )

    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    user = UserProfileSerializer(read_only=True)

    def validate(self, attrs):
        identifier = (
            attrs.get('identifier')
            or attrs.get('username')
            or attrs.get('email')
        )

        password = attrs.get('password')

        if not identifier:
            raise serializers.ValidationError({
                'identifier': 'Username or email is required.'
            })

        if not password:
            raise serializers.ValidationError({
                'password': 'Password is required.'
            })

        identifier = identifier.strip()

        user = User.objects.filter(
            Q(username__iexact=identifier) | Q(email__iexact=identifier.lower())
        ).first()

        if user is None:
            raise serializers.ValidationError('Invalid credentials.')

        authenticated_user = authenticate(
            username=user.username,
            password=password,
        )

        if authenticated_user is None:
            raise serializers.ValidationError('Invalid credentials.')

        if not authenticated_user.is_active:
            raise serializers.ValidationError('This account is inactive.')

        refresh = RefreshToken.for_user(authenticated_user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': authenticated_user,
        }


class TokenRefreshRequestSerializer(serializers.Serializer):
    """
    Request serializer for refreshing JWT access token.
    """

    refresh = serializers.CharField()


class TokenRefreshResponseSerializer(serializers.Serializer):
    """
    Response serializer for refreshed JWT access token.
    """

    access = serializers.CharField()


class RegisterResponseSerializer(serializers.Serializer):
    """
    Response serializer for successful registration.
    """

    message = serializers.CharField()
    user = UserProfileSerializer()


class LoginResponseSerializer(serializers.Serializer):
    """
    Response serializer for successful login.
    """

    message = serializers.CharField()
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserProfileSerializer()


class ProfileResponseSerializer(serializers.Serializer):
    """
    Response serializer for profile read/update.
    """

    message = serializers.CharField()
    user = UserProfileSerializer()