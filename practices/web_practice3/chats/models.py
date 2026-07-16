from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


def attachment_upload_path(instance, filename):
    """
    Generates upload path for message attachments.
    """
    conversation_id = 'unknown'

    if instance.message_id:
        conversation_id = instance.message.conversation_id

    return f'attachments/conversation_{conversation_id}/{filename}'


class Project(models.Model):
    """
    Represents a user workspace/project.

    Each project belongs to exactly one user and can contain multiple
    conversations.
    """

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='projects',
    )

    title = models.CharField(max_length=255)

    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_owned_by(self, user):
        return bool(
            user
            and user.is_authenticated
            and self.owner_id == user.id
        )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['title']),
        ]


class AIModel(models.Model):
    """
    Represents an available AI model in the system.

    Normal users can only read these records. Superusers will be allowed
    to create, update, or delete them later.
    """

    name = models.CharField(max_length=100)

    provider = models.CharField(max_length=100)

    description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    is_premium = models.BooleanField(
        default=False,
        help_text='If true, only premium users can use this model.',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_available_to(self, user):
        """
        Check whether a user can use this AI model.

        Free users can use only non-premium active models.
        Premium users can use active premium and non-premium models.
        """
        if not self.is_active:
            return False

        if not self.is_premium:
            return True

        return bool(
            user
            and user.is_authenticated
            and getattr(user, 'can_use_premium_features', False)
        )

    def __str__(self):
        return f'{self.provider} - {self.name}'

    class Meta:
        ordering = ['provider', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'provider'],
                name='unique_ai_model_per_provider',
            ),
        ]


class Assistant(models.Model):
    """
    Represents a custom or public assistant.

    Public assistants are available to all users.
    Private assistants belong to one specific user.
    """

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assistants',
        null=True,
        blank=True,
    )

    title = models.CharField(max_length=255)

    description = models.TextField(blank=True)

    system_prompt = models.TextField(
        help_text='Base instruction that defines the assistant behavior.',
    )

    is_public = models.BooleanField(
        default=False,
        help_text='Public assistants are available to every user.',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if not self.is_public and self.owner_id is None:
            raise ValidationError('Private assistants must have an owner.')

    def is_owned_by(self, user):
        return bool(
            user
            and user.is_authenticated
            and self.owner_id == user.id
        )

    def is_available_to(self, user):
        """
        Public assistants are available to authenticated users.
        Private assistants are only available to their owner.
        """
        if not user or not user.is_authenticated:
            return False

        if self.is_public:
            return True

        return self.is_owned_by(user)

    def can_be_modified_by(self, user):
        """
        Private assistants can be modified by their owner.
        Public assistants can only be modified by staff or superusers.
        """
        if not user or not user.is_authenticated:
            return False

        if user.is_staff or user.is_superuser:
            return True

        if self.is_public:
            return False

        return self.is_owned_by(user)

    def __str__(self):
        visibility = 'Public' if self.is_public else 'Private'
        return f'{self.title} ({visibility})'

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['is_public']),
        ]


class Conversation(models.Model):
    """
    Represents a chat conversation.

    Each conversation belongs to one user, can optionally belong to one project,
    and uses one AI model and optionally one assistant.
    """

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        ARCHIVED = 'archived', 'Archived'
        DELETED = 'deleted', 'Deleted'

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversations',
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='conversations',
        null=True,
        blank=True,
    )

    ai_model = models.ForeignKey(
        AIModel,
        on_delete=models.PROTECT,
        related_name='conversations',
    )

    assistant = models.ForeignKey(
        Assistant,
        on_delete=models.SET_NULL,
        related_name='conversations',
        null=True,
        blank=True,
    )

    title = models.CharField(max_length=255, blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.project_id and self.owner_id:
            if self.project.owner_id != self.owner_id:
                raise ValidationError('The selected project does not belong to this user.')

        if self.assistant_id and self.owner_id:
            if not self.assistant.is_public and self.assistant.owner_id != self.owner_id:
                raise ValidationError('The selected assistant is not available for this user.')

    def is_owned_by(self, user):
        return bool(
            user
            and user.is_authenticated
            and self.owner_id == user.id
        )

    def is_active_conversation(self):
        return self.status == self.Status.ACTIVE

    def soft_delete(self):
        self.status = self.Status.DELETED
        self.save(update_fields=['status', 'updated_at'])

    def __str__(self):
        return self.title or f'Conversation #{self.pk}'

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['project']),
            models.Index(fields=['status']),
        ]


class Message(models.Model):
    """
    Represents a message inside a conversation.

    Role can be user, system, or assistant.
    """

    class Role(models.TextChoices):
        USER = 'user', 'User'
        SYSTEM = 'system', 'System'
        ASSISTANT = 'assistant', 'Assistant'

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
    )

    content = models.TextField(blank=True)

    is_edited = models.BooleanField(default=False)

    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def owner(self):
        return self.conversation.owner

    @property
    def owner_id(self):
        return self.conversation.owner_id

    def is_owned_by(self, user):
        return bool(
            user
            and user.is_authenticated
            and self.owner_id == user.id
        )

    def soft_delete(self):
        self.is_deleted = True
        self.save(update_fields=['is_deleted', 'updated_at'])

    def __str__(self):
        preview = self.content[:50] if self.content else 'Empty message'
        return f'{self.role}: {preview}'

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation']),
            models.Index(fields=['role']),
            models.Index(fields=['created_at']),
        ]


class Attachment(models.Model):
    """
    Represents a file attached to a message.
    """

    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='attachments',
    )

    file = models.FileField(upload_to=attachment_upload_path)

    file_format = models.CharField(
        max_length=50,
        blank=True,
    )

    file_size = models.PositiveBigIntegerField(
        default=0,
        help_text='File size in bytes.',
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    @property
    def owner(self):
        return self.message.conversation.owner

    @property
    def owner_id(self):
        return self.message.conversation.owner_id

    @property
    def file_name(self):
        if not self.file:
            return ''
        return self.file.name.split('/')[-1]

    def is_owned_by(self, user):
        return bool(
            user
            and user.is_authenticated
            and self.owner_id == user.id
        )

    def save(self, *args, **kwargs):
        if self.file:
            if not self.file_size:
                self.file_size = self.file.size

            if not self.file_format:
                file_name = self.file.name
                if '.' in file_name:
                    self.file_format = file_name.rsplit('.', 1)[-1].lower()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.file_name or f'Attachment #{self.pk}'

    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['message']),
        ]