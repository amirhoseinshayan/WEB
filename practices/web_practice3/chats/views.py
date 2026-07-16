from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from rest_framework import parsers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import ListAPIView, ListCreateAPIView
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
    IsAttachmentOwner,
    IsConversationOwner,
    IsMessageOwner,
    IsOwner,
    IsPublicAssistantReadOnlyOrOwner,
)
from subscriptions.services import build_subscription_status, enforce_daily_message_limit

from .models import AIModel, Assistant, Attachment, Conversation, Message, Project
from .serializers import (
    AIModelSerializer,
    AssistantSerializer,
    AttachmentSerializer,
    AttachmentUploadSerializer,
    ConversationAssistantUpdateSerializer,
    ConversationSerializer,
    MessageCreateSerializer,
    MessageSerializer,
    MessageUpdateSerializer,
    ProjectSerializer,
    SendMessageResponseSerializer,
)
from .services import generate_mock_ai_response


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
    ),
    destroy=extend_schema(
        tags=['Projects'],
        summary='Delete a project',
        responses={204: OpenApiResponse(description='Project deleted successfully.')},
    ),
)
class ProjectViewSet(UserOwnedQuerySetMixin, OwnerCreateMixin, viewsets.ModelViewSet):
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
        responses={200: AIModelSerializer(many=True)},
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


@extend_schema_view(
    list=extend_schema(
        tags=['Messages'],
        summary='List current user messages',
        responses={200: MessageSerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=['Messages'],
        summary='Retrieve a message owned by current user',
        responses={
            200: MessageSerializer,
            404: OpenApiResponse(description='Message not found.'),
        },
    ),
    partial_update=extend_schema(
        tags=['Messages'],
        summary='Edit a user message',
        request=MessageUpdateSerializer,
        responses={
            200: MessageSerializer,
            400: OpenApiResponse(description='Only user messages can be edited.'),
        },
    ),
    destroy=extend_schema(
        tags=['Messages'],
        summary='Soft delete a message',
        responses={204: OpenApiResponse(description='Message soft deleted successfully.')},
    ),
)
class MessageViewSet(viewsets.ModelViewSet):
    """
    API for reading, editing, and deleting messages.

    Message creation must be done through:
    POST /api/conversations/<conversation_id>/messages/
    """

    permission_classes = [IsAuthenticated, IsMessageOwner]
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        return (
            Message.objects
            .select_related('conversation', 'conversation__owner')
            .prefetch_related('attachments')
            .annotate(attachments_count=Count('attachments'))
            .filter(conversation__owner=self.request.user, is_deleted=False)
            .order_by('created_at')
        )

    def get_serializer_class(self):
        if self.action == 'partial_update':
            return MessageUpdateSerializer

        return MessageSerializer

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response_serializer = MessageSerializer(
            instance,
            context={'request': request},
        )

        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        instance.soft_delete()


@extend_schema_view(
    get=extend_schema(
        tags=['Messages'],
        summary='Get paginated message history of a conversation',
        responses={
            200: MessageSerializer(many=True),
            404: OpenApiResponse(description='Conversation not found.'),
        },
    ),
    post=extend_schema(
        tags=['Messages'],
        summary='Send a message and receive a mock AI response',
        description=(
            'Free users are limited by their daily message quota. '
            'Premium users have unlimited daily messages.'
        ),
        request=MessageCreateSerializer,
        responses={
            201: SendMessageResponseSerializer,
            400: OpenApiResponse(description='Invalid message or inactive conversation.'),
            404: OpenApiResponse(description='Conversation not found.'),
            429: OpenApiResponse(description='Daily message limit exceeded.'),
        },
        examples=[
            OpenApiExample(
                name='Send Message Request',
                value={
                    'content': 'Hello, explain Django REST Framework shortly.',
                },
                request_only=True,
            )
        ],
    ),
)
class ConversationMessagesAPIView(ListCreateAPIView):
    """
    GET:
    Return message history of a conversation.

    POST:
    Store user's message and generate a mock assistant response.
    """

    permission_classes = [IsAuthenticated]

    def get_conversation(self):
        if hasattr(self, '_conversation'):
            return self._conversation

        conversation_id = self.kwargs.get('conversation_id')

        self._conversation = get_object_or_404(
            Conversation.objects.select_related('owner', 'ai_model', 'assistant'),
            id=conversation_id,
            owner=self.request.user,
        )

        if self._conversation.status == Conversation.Status.DELETED:
            raise ValidationError('This conversation is deleted.')

        return self._conversation

    def get_queryset(self):
        conversation = self.get_conversation()

        return (
            Message.objects
            .select_related('conversation', 'conversation__owner')
            .prefetch_related('attachments')
            .annotate(attachments_count=Count('attachments'))
            .filter(conversation=conversation, is_deleted=False)
            .order_by('created_at')
        )

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MessageCreateSerializer

        return MessageSerializer

    def create(self, request, *args, **kwargs):
        conversation = self.get_conversation()

        if conversation.status != Conversation.Status.ACTIVE:
            raise ValidationError('Messages can only be sent to active conversations.')

        if not conversation.ai_model.is_available_to(request.user):
            raise ValidationError({
                'ai_model': 'The selected AI model is not available for your current subscription.'
            })

        enforce_daily_message_limit(request.user)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        content = serializer.validated_data['content']

        with transaction.atomic():
            user_message = Message.objects.create(
                conversation=conversation,
                role=Message.Role.USER,
                content=content,
            )

            assistant_message = Message.objects.create(
                conversation=conversation,
                role=Message.Role.ASSISTANT,
                content=generate_mock_ai_response(conversation, user_message),
            )

            default_title = f'Conversation #{conversation.id}'

            if not conversation.title or conversation.title == default_title:
                conversation.title = content[:60]
                conversation.save(update_fields=['title', 'updated_at'])

        user_message = (
            Message.objects
            .select_related('conversation', 'conversation__owner')
            .annotate(attachments_count=Count('attachments'))
            .get(id=user_message.id)
        )

        assistant_message = (
            Message.objects
            .select_related('conversation', 'conversation__owner')
            .annotate(attachments_count=Count('attachments'))
            .get(id=assistant_message.id)
        )

        return Response(
            {
                'message': 'Message sent successfully.',
                'user_message': MessageSerializer(
                    user_message,
                    context={'request': request},
                ).data,
                'assistant_message': MessageSerializer(
                    assistant_message,
                    context={'request': request},
                ).data,
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema_view(
    list=extend_schema(
        tags=['Attachments'],
        summary='List current user attachments',
        responses={200: AttachmentSerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=['Attachments'],
        summary='Retrieve an attachment owned by current user',
        responses={
            200: AttachmentSerializer,
            404: OpenApiResponse(description='Attachment not found.'),
        },
    ),
    destroy=extend_schema(
        tags=['Attachments'],
        summary='Delete an attachment',
        responses={
            204: OpenApiResponse(description='Attachment deleted successfully.'),
            404: OpenApiResponse(description='Attachment not found.'),
        },
    ),
)
class AttachmentViewSet(viewsets.ModelViewSet):
    """
    API for listing, retrieving, and deleting attachments.

    Attachment upload must be done through:
    POST /api/messages/<message_id>/attachments/
    """

    serializer_class = AttachmentSerializer
    permission_classes = [IsAuthenticated, IsAttachmentOwner]
    http_method_names = ['get', 'delete', 'head', 'options']

    def get_queryset(self):
        return (
            Attachment.objects
            .select_related(
                'message',
                'message__conversation',
                'message__conversation__owner',
            )
            .filter(message__conversation__owner=self.request.user)
            .order_by('-uploaded_at')
        )

    def perform_destroy(self, instance):
        if instance.file:
            instance.file.delete(save=False)

        instance.delete()


@extend_schema_view(
    get=extend_schema(
        tags=['Attachments'],
        summary='List attachments of a specific message',
        responses={
            200: AttachmentSerializer(many=True),
            404: OpenApiResponse(description='Message not found.'),
        },
    ),
    post=extend_schema(
        tags=['Attachments'],
        summary='Upload an attachment to a user message - premium only',
        request=AttachmentUploadSerializer,
        responses={
            201: AttachmentSerializer,
            400: OpenApiResponse(description='Invalid file.'),
            403: OpenApiResponse(description='File upload is available for Premium users only.'),
            404: OpenApiResponse(description='Message not found.'),
        },
        examples=[
            OpenApiExample(
                name='Upload Attachment Request',
                value={
                    'file': 'example.pdf',
                },
                request_only=True,
            )
        ],
    ),
)
class MessageAttachmentsAPIView(ListCreateAPIView):
    """
    GET:
    List attachments for a specific message.

    POST:
    Upload an attachment to a user message.
    Only Premium users can upload files.
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def get_message(self):
        if hasattr(self, '_message'):
            return self._message

        message_id = self.kwargs.get('message_id')

        self._message = get_object_or_404(
            Message.objects.select_related('conversation', 'conversation__owner'),
            id=message_id,
            conversation__owner=self.request.user,
            is_deleted=False,
        )

        return self._message

    def get_queryset(self):
        message = self.get_message()

        return (
            Attachment.objects
            .select_related(
                'message',
                'message__conversation',
                'message__conversation__owner',
            )
            .filter(message=message)
            .order_by('-uploaded_at')
        )

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AttachmentUploadSerializer

        return AttachmentSerializer

    def create(self, request, *args, **kwargs):
        message = self.get_message()

        if message.role != Message.Role.USER:
            raise ValidationError(
                'Attachments can only be uploaded to user messages.'
            )

        subscription_status = build_subscription_status(request.user)

        if not subscription_status['can_upload_files']:
            raise PermissionDenied(
                'File upload is available for Premium users only.'
            )

        serializer = self.get_serializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)

        attachment = serializer.save(message=message)

        response_serializer = AttachmentSerializer(
            attachment,
            context={'request': request},
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )