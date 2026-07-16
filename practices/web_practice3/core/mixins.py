from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q
from rest_framework.exceptions import PermissionDenied


class UserOwnedQuerySetMixin:
    """
    Filters queryset so each user can only see their own objects.

    Usage example in future ViewSets:

        class ProjectViewSet(UserOwnedQuerySetMixin, ModelViewSet):
            queryset = Project.objects.all()
            owner_field = 'owner'

    For nested ownership, use:

        owner_field = 'conversation__owner'
    """

    owner_field = 'owner'
    allow_staff_all = False

    def get_queryset(self):
        queryset = super().get_queryset()
        return self.filter_queryset_by_user(queryset)

    def filter_queryset_by_user(self, queryset):
        user = self.request.user

        if not user or not user.is_authenticated:
            return queryset.none()

        if self.allow_staff_all and (user.is_staff or user.is_superuser):
            return queryset

        if not self.owner_field:
            raise ImproperlyConfigured(
                f'{self.__class__.__name__} must define owner_field.'
            )

        return queryset.filter(**{self.owner_field: user})


class OwnerCreateMixin:
    """
    Automatically saves the authenticated user as the owner of a new object.

    Usage example in future ViewSets:

        class ProjectViewSet(OwnerCreateMixin, ModelViewSet):
            owner_save_field = 'owner'
    """

    owner_save_field = 'owner'

    def perform_create(self, serializer):
        user = self.request.user

        if not user or not user.is_authenticated:
            raise PermissionDenied('Authentication is required.')

        if not self.owner_save_field:
            raise ImproperlyConfigured(
                f'{self.__class__.__name__} must define owner_save_field.'
            )

        serializer.save(**{self.owner_save_field: user})


class PublicOrOwnerAssistantQuerySetMixin:
    """
    Filters Assistant queryset.

    Rules:
    - authenticated users can see public assistants
    - authenticated users can see their own private assistants
    - staff users can optionally see all assistants
    """

    allow_staff_all = True

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if not user or not user.is_authenticated:
            return queryset.none()

        if self.allow_staff_all and (user.is_staff or user.is_superuser):
            return queryset

        return queryset.filter(
            Q(is_public=True) | Q(owner=user)
        )


class SoftDeleteMixin:
    """
    Soft delete mixin.

    If the object has a status field and a Status.DELETED choice,
    it will be marked as deleted instead of being physically removed.
    Otherwise, normal delete is used.
    """

    soft_delete_status_field = 'status'

    def perform_destroy(self, instance):
        status_field = self.soft_delete_status_field

        if hasattr(instance, status_field):
            status_class = getattr(instance, 'Status', None)
            deleted_value = getattr(status_class, 'DELETED', 'deleted')

            setattr(instance, status_field, deleted_value)
            instance.save(update_fields=[status_field, 'updated_at'])
            return

        instance.delete()


class ConversationNestedObjectMixin:
    """
    Helper mixin for nested routes under a conversation.

    It will be useful for endpoints like:

        /api/conversations/<conversation_id>/messages/

    It checks whether the selected conversation belongs to request.user.
    """

    conversation_lookup_url_kwarg = 'conversation_id'

    def get_conversation_id(self):
        conversation_id = self.kwargs.get(self.conversation_lookup_url_kwarg)

        if conversation_id is None:
            raise ImproperlyConfigured(
                f'{self.__class__.__name__} requires '
                f'{self.conversation_lookup_url_kwarg} in URL kwargs.'
            )

        return conversation_id

    def filter_queryset_by_conversation_owner(self, queryset):
        user = self.request.user

        if not user or not user.is_authenticated:
            return queryset.none()

        return queryset.filter(
            conversation_id=self.get_conversation_id(),
            conversation__owner=user,
        )


class ProjectNestedConversationMixin:
    """
    Helper mixin for nested project conversation routes.

    It will be useful for endpoints like:

        /api/projects/<project_id>/conversations/
    """

    project_lookup_url_kwarg = 'project_id'

    def get_project_id(self):
        project_id = self.kwargs.get(self.project_lookup_url_kwarg)

        if project_id is None:
            raise ImproperlyConfigured(
                f'{self.__class__.__name__} requires '
                f'{self.project_lookup_url_kwarg} in URL kwargs.'
            )

        return project_id

    def filter_queryset_by_project_owner(self, queryset):
        user = self.request.user

        if not user or not user.is_authenticated:
            return queryset.none()

        return queryset.filter(
            project_id=self.get_project_id(),
            project__owner=user,
        )