from django.db.models import Count
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.mixins import (
    OwnerCreateMixin,
    PublicOrOwnerAssistantQuerySetMixin,
    SoftDeleteMixin,
    UserOwnedQuerySetMixin,
)
from core.permissions import (
    IsAdminOrReadOnly,
    IsConversationOwner,
    IsOwner,
    IsPublicAssistantReadOnlyOrOwner,
)

from .models import AIModel, Assistant, Conversation, Project
from .serializers import (
    AIModelSerializer,
    AssistantSerializer,
    ConversationAssistantUpdateSerializer,
    ConversationSerializer,
    ProjectSerializer,
)


@extend_schema_view(
    list=extend_schema(
        tags=['Projects'],
        summary='List current user projects',
        responses={200: ProjectSerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=['Projects'],
        summary='Retrieve a project owned by current user',
        responses={
            200: ProjectSerializer,
            404: OpenApiResponse(description='Project not found.'),
        },
    ),
    create=extend_schema(
        tags=['Projects'],
        summary='Create a new project',
        request=ProjectSerializer,
        responses={201: ProjectSerializer},
        examples=[
            OpenApiExample(
                name='Create Project Request',
                value={
                    'title': 'University Project',
                    'description': 'Chats related to my university assignment.',
                },
                request_only=True,
            )
        ],
    ),
    update=extend_schema(
        tags=['Projects'],
        summary='Fully update a project',
        request=ProjectSerializer,
        responses={200: ProjectSerializer},
    ),
    partial_update=extend_schema(
        tags=['Projects'],
        summary='Partially update a project',
        request=ProjectSerializer,
        responses={200: ProjectSerializer},
        examples=[
            OpenApiExample(
                name='Update Project Request',
                value={
                    'title': 'Updated University Project',
                },
                request_only=True,
            )
        ],
    ),
    destroy=extend_schema(
        tags=['Projects'],
        summary='Delete a project',
        responses={204: OpenApiResponse(description='Project deleted successfully.')},
    ),
)
class ProjectViewSet(UserOwnedQuerySetMixin, OwnerCreateMixin, viewsets.ModelViewSet):
    """
    CRUD API for projects.

    Users can only access their own projects.
    """

    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    owner_field = 'owner'
    owner_save_field = 'owner'

    def get_queryset(self):
        return (
            Project.objects
            .annotate(conversations_count=Count('conversations'))
            .select_related('owner')
            .order_by('-created_at')
            .filter(owner=self.request.user)
        )


@extend_schema_view(
    list=extend_schema(
        tags=['AI Models'],
        summary='List active AI models',
        description=(
            'Returns active AI models. The field '
            '`is_available_for_current_user` shows whether the authenticated '
            'user can select each model. Premium models return false for free users.'
        ),
        responses={200: AIModelSerializer(many=True)},
        examples=[
            OpenApiExample(
                name='AI Models List Response',
                value={
                    'count': 4,
                    'next': None,
                    'previous': None,
                    'results': [
                        {
                            'id': 1,
                            'name': 'GPT-3.5',
                            'provider': 'OpenAI',
                            'description': 'Basic free model for regular users.',
                            'is_active': True,
                            'is_premium': False,
                            'is_available_for_current_user': True,
                            'created_at': '2026-01-01T10:00:00Z',
                            'updated_at': '2026-01-01T10:00:00Z',
                        },
                        {
                            'id': 2,
                            'name': 'GPT-4',
                            'provider': 'OpenAI',
                            'description': 'Premium model with stronger reasoning capabilities.',
                            'is_active': True,
                            'is_premium': True,
                            'is_available_for_current_user': False,
                            'created_at': '2026-01-01T10:00:00Z',
                            'updated_at': '2026-01-01T10:00:00Z',
                        },
                    ],
                },
                response_only=True,
                status_codes=['200'],
            )
        ],
    ),
    retrieve=extend_schema(
        tags=['AI Models'],
        summary='Retrieve an AI model',
        responses={
            200: AIModelSerializer,
            404: OpenApiResponse(description='AI model not found.'),
        },
    ),
    create=extend_schema(
        tags=['AI Models'],
        summary='Create a new AI model - admin only',
        request=AIModelSerializer,
        responses={
            201: AIModelSerializer,
            403: OpenApiResponse(description='Only admins can create models.'),
        },
        examples=[
            OpenApiExample(
                name='Create AI Model Request',
                value={
                    'name': 'GPT-4',
                    'provider': 'OpenAI',
                    'description': 'Premium reasoning model',
                    'is_active': True,
                    'is_premium': True,
                },
                request_only=True,
            )
        ],
    ),
    update=extend_schema(
        tags=['AI Models'],
        summary='Fully update an AI model - admin only',
        request=AIModelSerializer,
        responses={200: AIModelSerializer},
    ),
    partial_update=extend_schema(
        tags=['AI Models'],
        summary='Partially update an AI model - admin only',
        request=AIModelSerializer,
        responses={200: AIModelSerializer},
    ),
    destroy=extend_schema(
        tags=['AI Models'],
        summary='Delete an AI model - admin only',
        responses={204: OpenApiResponse(description='AI model deleted successfully.')},
    ),
)
class AIModelViewSet(viewsets.ModelViewSet):
    """
    CRUD API for AI models.

    Authenticated users can read active models.
    Only staff/superusers can create, update, or delete AI models.
    """

    serializer_class = AIModelSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = AIModel.objects.all().order_by('provider', 'name')

        user = self.request.user

        if user.is_staff or user.is_superuser:
            return queryset

        return queryset.filter(is_active=True)


@extend_schema_view(
    list=extend_schema(
        tags=['Assistants'],
        summary='List public assistants and current user private assistants',
        responses={200: AssistantSerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=['Assistants'],
        summary='Retrieve an available assistant',
        responses={
            200: AssistantSerializer,
            404: OpenApiResponse(description='Assistant not found.'),
        },
    ),
    create=extend_schema(
        tags=['Assistants'],
        summary='Create a private assistant',
        request=AssistantSerializer,
        responses={201: AssistantSerializer},
        examples=[
            OpenApiExample(
                name='Create Assistant Request',
                value={
                    'title': 'Coding Assistant',
                    'description': 'Helps with programming questions.',
                    'system_prompt': 'You are a helpful coding assistant.',
                    'is_public': False,
                },
                request_only=True,
            )
        ],
    ),
    update=extend_schema(
        tags=['Assistants'],
        summary='Fully update an assistant',
        request=AssistantSerializer,
        responses={200: AssistantSerializer},
    ),
    partial_update=extend_schema(
        tags=['Assistants'],
        summary='Partially update an assistant',
        request=AssistantSerializer,
        responses={200: AssistantSerializer},
    ),
    destroy=extend_schema(
        tags=['Assistants'],
        summary='Delete an assistant',
        responses={204: OpenApiResponse(description='Assistant deleted successfully.')},
    ),
)
class AssistantViewSet(PublicOrOwnerAssistantQuerySetMixin, viewsets.ModelViewSet):
    """
    CRUD API for assistants.

    Rules:
    - Users can see public assistants.
    - Users can see and manage their own private assistants.
    - Normal users cannot create public assistants.
    - Public assistants can only be modified by admins.
    """

    serializer_class = AssistantSerializer
    permission_classes = [IsAuthenticated, IsPublicAssistantReadOnlyOrOwner]

    def get_queryset(self):
        queryset = (
            Assistant.objects
            .select_related('owner')
            .order_by('-created_at')
        )

        user = self.request.user

        if user.is_staff or user.is_superuser:
            return queryset

        return queryset.filter_public_or_owned(user)

    def perform_create(self, serializer):
        is_public = serializer.validated_data.get('is_public', False)

        if is_public and not (self.request.user.is_staff or self.request.user.is_superuser):
            raise PermissionDenied('Only administrators can create public assistants.')

        if is_public:
            serializer.save(owner=None)
            return

        serializer.save(owner=self.request.user)

    @extend_schema(
        tags=['Assistants'],
        summary='List public assistants only',
        responses={200: AssistantSerializer(many=True)},
    )
    @action(detail=False, methods=['get'], url_path='public')
    def public(self, request):
        """
        List only public assistants.
        """
        queryset = (
            Assistant.objects
            .filter(is_public=True)
            .select_related('owner')
            .order_by('-created_at')
        )

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=['Assistants'],
        summary='List current user private assistants only',
        responses={200: AssistantSerializer(many=True)},
    )
    @action(detail=False, methods=['get'], url_path='mine')
    def mine(self, request):
        """
        List only private assistants owned by the current user.
        """
        queryset = (
            Assistant.objects
            .filter(owner=request.user, is_public=False)
            .select_related('owner')
            .order_by('-created_at')
        )

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema_view(
    list=extend_schema(
        tags=['Conversations'],
        summary='List current user conversations',
        responses={200: ConversationSerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=['Conversations'],
        summary='Retrieve a conversation owned by current user',
        responses={
            200: ConversationSerializer,
            404: OpenApiResponse(description='Conversation not found.'),
        },
    ),
    create=extend_schema(
        tags=['Conversations'],
        summary='Create a new conversation',
        request=ConversationSerializer,
        responses={201: ConversationSerializer},
        examples=[
            OpenApiExample(
                name='Create Conversation Request',
                value={
                    'project': 1,
                    'ai_model': 1,
                    'assistant': 1,
                    'title': 'My first chat',
                },
                request_only=True,
            )
        ],
    ),
    update=extend_schema(
        tags=['Conversations'],
        summary='Fully update a conversation',
        request=ConversationSerializer,
        responses={200: ConversationSerializer},
    ),
    partial_update=extend_schema(
        tags=['Conversations'],
        summary='Partially update a conversation',
        request=ConversationSerializer,
        responses={200: ConversationSerializer},
        examples=[
            OpenApiExample(
                name='Update Conversation Request',
                value={
                    'title': 'Updated chat title',
                },
                request_only=True,
            )
        ],
    ),
    destroy=extend_schema(
        tags=['Conversations'],
        summary='Soft delete a conversation',
        responses={204: OpenApiResponse(description='Conversation soft deleted successfully.')},
    ),
)
class ConversationViewSet(
    UserOwnedQuerySetMixin,
    OwnerCreateMixin,
    SoftDeleteMixin,
    viewsets.ModelViewSet,
):
    """
    CRUD API for conversations.

    Users can only access their own conversations.
    Delete is implemented as soft delete by changing status to deleted.
    """

    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsConversationOwner]
    owner_field = 'owner'
    owner_save_field = 'owner'
    soft_delete_status_field = 'status'

    def get_queryset(self):
        return (
            Conversation.objects
            .select_related('owner', 'project', 'ai_model', 'assistant')
            .annotate(messages_count=Count('messages'))
            .filter(owner=self.request.user)
            .exclude(status=Conversation.Status.DELETED)
            .order_by('-created_at')
        )

    def perform_create(self, serializer):
        conversation = serializer.save(owner=self.request.user)

        if not conversation.title:
            conversation.title = f'Conversation #{conversation.id}'
            conversation.save(update_fields=['title', 'updated_at'])

    @extend_schema(
        tags=['Conversations'],
        summary='Select, change, or clear assistant for a conversation',
        request=ConversationAssistantUpdateSerializer,
        responses={
            200: ConversationSerializer,
            400: OpenApiResponse(description='Selected assistant is not available.'),
            404: OpenApiResponse(description='Conversation not found.'),
        },
        examples=[
            OpenApiExample(
                name='Select Assistant Request',
                value={
                    'assistant': 1,
                },
                request_only=True,
            ),
            OpenApiExample(
                name='Clear Assistant Request',
                value={
                    'assistant': None,
                },
                request_only=True,
            ),
        ],
    )
    @action(detail=True, methods=['patch'], url_path='assistant')
    def assistant(self, request, pk=None):
        """
        Select, change, or clear assistant for a conversation.
        """
        conversation = self.get_object()

        serializer = ConversationAssistantUpdateSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)

        conversation.assistant = serializer.validated_data['assistant']
        conversation.save(update_fields=['assistant', 'updated_at'])

        response_serializer = ConversationSerializer(
            conversation,
            context={'request': request},
        )

        return Response(response_serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Projects'],
    summary='List conversations for a specific project',
    responses={
        200: ConversationSerializer(many=True),
        404: OpenApiResponse(description='Project not found.'),
    },
)
class ProjectConversationsAPIView(ListAPIView):
    """
    List conversations that belong to a specific project owned by the current user.
    """

    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        project_id = self.kwargs.get('project_id')

        return (
            Conversation.objects
            .select_related('owner', 'project', 'ai_model', 'assistant')
            .annotate(messages_count=Count('messages'))
            .filter(
                owner=self.request.user,
                project_id=project_id,
            )
            .exclude(status=Conversation.Status.DELETED)
            .order_by('-created_at')
        )