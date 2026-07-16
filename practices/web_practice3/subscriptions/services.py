from datetime import timedelta

from django.utils import timezone
from rest_framework.exceptions import Throttled

from .models import SubscriptionPlan


DEFAULT_FREE_DAILY_MESSAGE_LIMIT = 50


def get_effective_subscription_type(user):
    """
    Return the user's effective subscription type.

    If premium_until is expired, the user is treated as free.
    """
    if user and user.is_authenticated and user.is_premium:
        return SubscriptionPlan.PlanType.PREMIUM

    return SubscriptionPlan.PlanType.FREE


def get_active_subscription_plan_for_user(user):
    """
    Return the active subscription plan that matches the user's current status.

    Since the User model stores subscription_type and premium_until but does not
    store the exact purchased plan, this helper returns the first active plan
    matching the effective subscription type.
    """
    plan_type = get_effective_subscription_type(user)

    return (
        SubscriptionPlan.objects
        .filter(plan_type=plan_type, is_active=True)
        .order_by('price', 'name')
        .first()
    )


def get_current_day_range():
    """
    Return start and end datetimes for the current local day.
    """
    now = timezone.localtime(timezone.now())

    start = now.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    end = start + timedelta(days=1)

    return start, end


def get_user_daily_message_usage(user):
    """
    Count how many user messages the user has sent today.

    Only messages with role='user' are counted.
    Assistant mock responses are not counted against the user's limit.
    """
    if not user or not user.is_authenticated:
        return 0

    from chats.models import Message

    start, end = get_current_day_range()

    return (
        Message.objects
        .filter(
            conversation__owner=user,
            role=Message.Role.USER,
            created_at__gte=start,
            created_at__lt=end,
        )
        .count()
    )


def get_user_daily_message_limit(user):
    """
    Return the daily message limit for the user.

    Premium users have unlimited messages, represented by None.
    Free users use the active Free Plan limit.
    If no Free Plan exists, a safe default limit is used.
    """
    if not user or not user.is_authenticated:
        return DEFAULT_FREE_DAILY_MESSAGE_LIMIT

    if user.is_premium:
        return None

    free_plan = (
        SubscriptionPlan.objects
        .filter(
            plan_type=SubscriptionPlan.PlanType.FREE,
            is_active=True,
        )
        .order_by('price', 'name')
        .first()
    )

    if free_plan is None:
        return DEFAULT_FREE_DAILY_MESSAGE_LIMIT

    if free_plan.daily_message_limit is None:
        return None

    return free_plan.daily_message_limit


def get_user_remaining_daily_messages(user):
    """
    Return remaining daily messages for the user.

    None means unlimited.
    """
    limit = get_user_daily_message_limit(user)

    if limit is None:
        return None

    used = get_user_daily_message_usage(user)
    remaining = limit - used

    return max(remaining, 0)


def enforce_daily_message_limit(user):
    """
    Enforce daily message limit before sending a new user message.

    Raises DRF Throttled exception with HTTP 429 if the user has reached
    the daily message limit.
    """
    limit = get_user_daily_message_limit(user)

    if limit is None:
        return

    used = get_user_daily_message_usage(user)

    if used >= limit:
        raise Throttled(
            detail=(
                'Daily message limit exceeded for Free plan. '
                'Upgrade to Premium for unlimited messages.'
            )
        )


def apply_subscription_plan_to_user(user, plan):
    """
    Apply a selected subscription plan to a user.

    Free plan:
    - subscription_type = free
    - premium_until = None

    Premium plan:
    - subscription_type = premium
    - premium_until = now + duration_days
    - if duration_days is 0, premium access is unlimited
    """
    if plan.plan_type == SubscriptionPlan.PlanType.FREE:
        user.subscription_type = user.SubscriptionType.FREE
        user.premium_until = None
        user.save(update_fields=['subscription_type', 'premium_until', 'updated_at'])
        return user

    user.subscription_type = user.SubscriptionType.PREMIUM

    if plan.duration_days and plan.duration_days > 0:
        user.premium_until = timezone.now() + timedelta(days=plan.duration_days)
    else:
        user.premium_until = None

    user.save(update_fields=['subscription_type', 'premium_until', 'updated_at'])

    return user


def build_subscription_status(user):
    """
    Build a complete subscription status dictionary for API responses.
    """
    current_plan = get_active_subscription_plan_for_user(user)
    effective_type = get_effective_subscription_type(user)
    daily_limit = get_user_daily_message_limit(user)
    daily_used = get_user_daily_message_usage(user)
    daily_remaining = get_user_remaining_daily_messages(user)

    if current_plan is not None:
        can_use_premium_models = current_plan.can_use_premium_models
        can_upload_files = current_plan.can_upload_files
        plan_name = current_plan.name
    else:
        can_use_premium_models = user.is_premium
        can_upload_files = user.is_premium
        plan_name = 'Premium' if user.is_premium else 'Free'

    return {
        'subscription_type': effective_type,
        'plan_name': plan_name,
        'is_premium': user.is_premium,
        'premium_until': user.premium_until,
        'daily_message_limit': daily_limit,
        'daily_messages_used': daily_used,
        'daily_messages_remaining': daily_remaining,
        'can_use_premium_models': can_use_premium_models,
        'can_upload_files': can_upload_files,
    }