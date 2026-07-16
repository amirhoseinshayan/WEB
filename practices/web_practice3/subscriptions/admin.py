from django.contrib import admin

from .models import SubscriptionPlan


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'plan_type',
        'price',
        'duration_days',
        'daily_message_limit',
        'can_use_premium_models',
        'can_upload_files',
        'is_active',
    )

    list_filter = (
        'plan_type',
        'can_use_premium_models',
        'can_upload_files',
        'is_active',
    )

    search_fields = (
        'name',
        'description',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    ordering = (
        'price',
        'name',
    )