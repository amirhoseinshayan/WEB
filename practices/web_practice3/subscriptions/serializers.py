from rest_framework import serializers

from accounts.serializers import UserProfileSerializer

from .models import SubscriptionPlan


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """
    Serializer for subscription plans.
    """

    is_free = serializers.BooleanField(read_only=True)
    is_premium = serializers.BooleanField(read_only=True)

    class Meta:
        model = SubscriptionPlan
        fields = (
            'id',
            'name',
            'plan_type',
            'description',
            'price',
            'duration_days',
            'daily_message_limit',
            'can_use_premium_models',
            'can_upload_files',
            'is_active',
            'is_free',
            'is_premium',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'is_active',
            'is_free',
            'is_premium',
            'created_at',
            'updated_at',
        )


class SubscriptionStatusSerializer(serializers.Serializer):
    """
    Serializer for current user's subscription status.
    """

    subscription_type = serializers.CharField()
    plan_name = serializers.CharField()
    is_premium = serializers.BooleanField()
    premium_until = serializers.DateTimeField(allow_null=True)
    daily_message_limit = serializers.IntegerField(allow_null=True)
    daily_messages_used = serializers.IntegerField()
    daily_messages_remaining = serializers.IntegerField(allow_null=True)
    can_use_premium_models = serializers.BooleanField()
    can_upload_files = serializers.BooleanField()


class PurchaseSubscriptionSerializer(serializers.Serializer):
    """
    Serializer for simulated subscription purchase.

    The user sends the selected plan_id.
    """

    plan_id = serializers.PrimaryKeyRelatedField(
        queryset=SubscriptionPlan.objects.filter(is_active=True),
        source='plan',
    )


class PurchaseSubscriptionResponseSerializer(serializers.Serializer):
    """
    Serializer for purchase response.
    """

    message = serializers.CharField()
    plan = SubscriptionPlanSerializer()
    user = UserProfileSerializer()
    subscription_status = SubscriptionStatusSerializer()