from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.utils import timezone


class User(AbstractUser):
    """
    Custom user model for the ChatGPT-like backend.

    This model extends Django's AbstractUser and adds subscription-related
    fields required by the assignment.
    """

    class SubscriptionType(models.TextChoices):
        FREE = 'free', 'Free'
        PREMIUM = 'premium', 'Premium'

    email = models.EmailField(unique=True)

    subscription_type = models.CharField(
        max_length=20,
        choices=SubscriptionType.choices,
        default=SubscriptionType.FREE,
    )

    premium_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text='If set, premium access is valid until this datetime.',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_premium(self):
        """
        Returns True if the user has an active premium subscription.
        """
        if self.subscription_type != self.SubscriptionType.PREMIUM:
            return False

        if self.premium_until is None:
            return True

        return self.premium_until > timezone.now()

    @property
    def can_use_premium_features(self):
        """
        Helper property used later for premium models, uploads, and limits.
        """
        return self.is_premium

    def __str__(self):
        return self.username


class LinkedAccount(models.Model):
    """
    Represents a trusted link between two user accounts.

    Later, this model will be used to issue a new JWT token for switching
    from one linked account to another.
    """

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_account_links',
    )

    linked_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='linked_to_accounts',
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.owner_id and self.linked_user_id and self.owner_id == self.linked_user_id:
            raise ValidationError('A user cannot link an account to itself.')

    def __str__(self):
        return f'{self.owner} -> {self.linked_user}'

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['owner', 'linked_user'],
                name='unique_linked_account_per_owner',
            ),
            models.CheckConstraint(
                condition=~Q(owner=F('linked_user')),
                name='prevent_self_account_link',
            ),
        ]