from django.db import models


class SubscriptionPlan(models.Model):
    """
    Represents a purchasable subscription plan.

    Free and Premium users will be handled later using this model.
    """

    class PlanType(models.TextChoices):
        FREE = 'free', 'Free'
        PREMIUM = 'premium', 'Premium'

    name = models.CharField(max_length=100, unique=True)

    plan_type = models.CharField(
        max_length=20,
        choices=PlanType.choices,
        default=PlanType.FREE,
    )

    description = models.TextField(blank=True)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    duration_days = models.PositiveIntegerField(
        default=30,
        help_text='Duration of the plan in days. Use 0 for unlimited or free default plans.',
    )

    daily_message_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Null means unlimited daily messages.',
    )

    can_use_premium_models = models.BooleanField(default=False)

    can_upload_files = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_free(self):
        return self.plan_type == self.PlanType.FREE

    @property
    def is_premium(self):
        return self.plan_type == self.PlanType.PREMIUM

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['price', 'name']