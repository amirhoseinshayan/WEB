from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import LinkedAccount, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'subscription_type',
        'premium_until',
        'is_staff',
        'is_active',
    )

    list_filter = (
        'subscription_type',
        'is_staff',
        'is_active',
        'is_superuser',
    )

    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name',
    )

    ordering = ('id',)

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            'Subscription Information',
            {
                'fields': (
                    'subscription_type',
                    'premium_until',
                )
            },
        ),
        (
            'Timestamps',
            {
                'fields': (
                    'created_at',
                    'updated_at',
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            'Additional Information',
            {
                'fields': (
                    'email',
                    'subscription_type',
                )
            },
        ),
    )


@admin.register(LinkedAccount)
class LinkedAccountAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'owner',
        'linked_user',
        'is_active',
        'created_at',
    )

    list_filter = (
        'is_active',
        'created_at',
    )

    search_fields = (
        'owner__username',
        'owner__email',
        'linked_user__username',
        'linked_user__email',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    ordering = ('-created_at',)