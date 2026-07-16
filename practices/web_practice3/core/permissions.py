from rest_framework.permissions import BasePermission, SAFE_METHODS


def is_authenticated_user(user):
    """
    Return True if the request user is authenticated.
    """
    return bool(user and user.is_authenticated)


def get_owner_id(obj):
    """
    Return owner id from an object.

    This helper supports objects that have:
    - owner_id field
    - owner attribute
    - custom owner property
    """
    if obj is None:
        return None

    if hasattr(obj, 'owner_id'):
        return getattr(obj, 'owner_id')

    owner = getattr(obj, 'owner', None)

    if owner is None:
        return None

    return getattr(owner, 'id', None)


def is_object_owner(obj, user):
    """
    Check whether the given user owns the given object.
    """
    if not is_authenticated_user(user):
        return False

    owner_id = get_owner_id(obj)

    if owner_id is None:
        return False

    return owner_id == user.id


class IsOwner(BasePermission):
    """
    Allows access only to the owner of the object.

    This permission expects the object to have an owner or owner_id attribute.
    """

    message = 'You do not have permission to access this object.'

    def has_permission(self, request, view):
        return is_authenticated_user(request.user)

    def has_object_permission(self, request, view, obj):
        return is_object_owner(obj, request.user)


class IsOwnerOrReadOnly(BasePermission):
    """
    Allows read-only access for safe methods and write access only for owners.

    This permission is useful when a resource may be visible but only editable
    by its owner.
    """

    message = 'You do not have permission to modify this object.'

    def has_permission(self, request, view):
        return is_authenticated_user(request.user)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return is_object_owner(obj, request.user)


class IsAdminOrReadOnly(BasePermission):
    """
    Allows read-only access to authenticated users and write access only to admins.

    This will be useful for AIModel endpoints:
    - normal users can list/read models
    - only staff/superusers can create/update/delete models
    """

    message = 'Only administrators can modify this resource.'

    def has_permission(self, request, view):
        if not is_authenticated_user(request.user):
            return False

        if request.method in SAFE_METHODS:
            return True

        return bool(request.user.is_staff or request.user.is_superuser)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return bool(request.user.is_staff or request.user.is_superuser)


class IsSelfOrAdmin(BasePermission):
    """
    Allows users to access only their own user object.
    Admin users can access every user object.
    """

    message = 'You can only access your own user profile.'

    def has_permission(self, request, view):
        return is_authenticated_user(request.user)

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True

        return getattr(obj, 'id', None) == request.user.id


class IsPublicAssistantReadOnlyOrOwner(BasePermission):
    """
    Permission for Assistant objects.

    Rules:
    - Public assistants can be read by authenticated users.
    - Private assistants can be read only by their owner.
    - Private assistants can be modified only by their owner.
    - Public assistants can be modified only by admin users.
    """

    message = 'You do not have permission to access this assistant.'

    def has_permission(self, request, view):
        return is_authenticated_user(request.user)

    def has_object_permission(self, request, view, obj):
        is_admin = bool(request.user.is_staff or request.user.is_superuser)
        is_owner = is_object_owner(obj, request.user)
        is_public = bool(getattr(obj, 'is_public', False))

        if request.method in SAFE_METHODS:
            return is_public or is_owner or is_admin

        if is_public:
            return is_admin

        return is_owner or is_admin


class IsConversationOwner(BasePermission):
    """
    Allows access only to the owner of a conversation.
    """

    message = 'You do not have permission to access this conversation.'

    def has_permission(self, request, view):
        return is_authenticated_user(request.user)

    def has_object_permission(self, request, view, obj):
        return is_object_owner(obj, request.user)


class IsMessageOwner(BasePermission):
    """
    Allows access only to the owner of the conversation that contains the message.
    """

    message = 'You do not have permission to access this message.'

    def has_permission(self, request, view):
        return is_authenticated_user(request.user)

    def has_object_permission(self, request, view, obj):
        return is_object_owner(obj, request.user)


class IsAttachmentOwner(BasePermission):
    """
    Allows access only to the owner of the message that contains the attachment.
    """

    message = 'You do not have permission to access this attachment.'

    def has_permission(self, request, view):
        return is_authenticated_user(request.user)

    def has_object_permission(self, request, view, obj):
        return is_object_owner(obj, request.user)


class IsLinkedAccountOwner(BasePermission):
    """
    Allows access only to the user who owns the linked account relation.
    """

    message = 'You do not have permission to access this linked account.'

    def has_permission(self, request, view):
        return is_authenticated_user(request.user)

    def has_object_permission(self, request, view, obj):
        return is_object_owner(obj, request.user)