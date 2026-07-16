from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import AIModel, Assistant, Conversation, Message, Project


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for user projects/workspaces.
    """

    owner = serializers.IntegerField(source='owner_id', read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    conversations_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Project
        fields = (
            'id',
            'owner',
            'owner_username',
            'title',
            'description',
            'conversations_count',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'owner',
            'owner_username',
            'conversations_count',
            'created_at',
            'updated_at',
        )

    def validate_title(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError('Project title cannot be empty.')

        return value


class AIModelSerializer(serializers.ModelSerializer):
    """
    Serializer for AI models.
    """

    is_available_for_current_user = serializers.SerializerMethodField()

    class Meta:
        model = AIModel
        fields = (
            'id',
            'name',
            'provider',
            'description',
            'is_active',
            'is_premium',
            'is_available_for_current_user',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'is_available_for_current_user',
            'created_at',
            'updated_at',
        )

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_is_available_for_current_user(self, obj):
        request = self.context.get('request')

        if request is None:
            return False

        return obj.is_available_to(request.user)

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError('Model name cannot be empty.')

        return value

    def validate_provider(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError('Provider cannot be empty.')

        return value


class AssistantSerializer(serializers.ModelSerializer):
    """
    Serializer for public and private assistants.
    """

    owner = serializers.IntegerField(source='owner_id', read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    is_available_for_current_user = serializers.SerializerMethodField()
    can_modify_current_user = serializers.SerializerMethodField()

    class Meta:
        model = Assistant
        fields = (
            'id',
            'owner',
            'owner_username',
            'title',
            'description',
            'system_prompt',
            'is_public',
            'is_available_for_current_user',
            'can_modify_current_user',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'owner',
            'owner_username',
            'is_available_for_current_user',
            'can_modify_current_user',
            'created_at',
            'updated_at',
        )

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_is_available_for_current_user(self, obj):
        request = self.context.get('request')

        if request is None:
            return False

        return obj.is_available_to(request.user)

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_can_modify_current_user(self, obj):
        request = self.context.get('request')

        if request is None:
            return False

        return obj.can_be_modified_by(request.user)

    def validate_title(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError('Assistant title cannot be empty.')

        return value

    def validate_system_prompt(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError('System prompt cannot be empty.')

        return value

    def validate(self, attrs):
        request = self.context.get('request')

        if request is None or not request.user.is_authenticated:
            raise serializers.ValidationError('Authentication is required.')

        is_public = attrs.get(
            'is_public',
            getattr(self.instance, 'is_public', False),
        )

        if is_public and not (request.user.is_staff or request.user.is_superuser):
            raise serializers.ValidationError({
                'is_public': 'Only administrators can create or modify public assistants.'
            })

        return attrs


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for conversations.
    """

    owner = serializers.IntegerField(source='owner_id', read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True)

    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(),
        required=False,
        allow_null=True,
    )

    ai_model = serializers.PrimaryKeyRelatedField(
        queryset=AIModel.objects.all(),
        required=True,
    )

    assistant = serializers.PrimaryKeyRelatedField(
        queryset=Assistant.objects.all(),
        required=False,
        allow_null=True,
    )

    project_title = serializers.CharField(source='project.title', read_only=True)
    ai_model_name = serializers.CharField(source='ai_model.name', read_only=True)
    assistant_title = serializers.CharField(source='assistant.title', read_only=True)
    messages_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Conversation
        fields = (
            'id',
            'owner',
            'owner_username',
            'project',
            'project_title',
            'ai_model',
            'ai_model_name',
            'assistant',
            'assistant_title',
            'title',
            'status',
            'messages_count',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'owner',
            'owner_username',
            'project_title',
            'ai_model_name',
            'assistant_title',
            'messages_count',
            'created_at',
            'updated_at',
        )

    def validate_title(self, value):
        return value.strip()

    def validate(self, attrs):
        request = self.context.get('request')

        if request is None or not request.user.is_authenticated:
            raise serializers.ValidationError('Authentication is required.')

        user = request.user

        project = attrs.get(
            'project',
            getattr(self.instance, 'project', None),
        )

        ai_model = attrs.get(
            'ai_model',
            getattr(self.instance, 'ai_model', None),
        )

        assistant = attrs.get(
            'assistant',
            getattr(self.instance, 'assistant', None),
        )

        if project is not None and project.owner_id != user.id:
            raise serializers.ValidationError({
                'project': 'The selected project does not belong to you.'
            })

        if ai_model is not None and not ai_model.is_available_to(user):
            raise serializers.ValidationError({
                'ai_model': 'The selected AI model is not available for your account.'
            })

        if assistant is not None and not assistant.is_available_to(user):
            raise serializers.ValidationError({
                'assistant': 'The selected assistant is not available for your account.'
            })

        return attrs


class ConversationAssistantUpdateSerializer(serializers.Serializer):
    """
    Serializer for selecting, changing, or clearing the assistant of a conversation.
    """

    assistant = serializers.PrimaryKeyRelatedField(
        queryset=Assistant.objects.all(),
        required=True,
        allow_null=True,
    )

    def validate_assistant(self, value):
        request = self.context.get('request')

        if request is None or not request.user.is_authenticated:
            raise serializers.ValidationError('Authentication is required.')

        if value is not None and not value.is_available_to(request.user):
            raise serializers.ValidationError(
                'The selected assistant is not available for your account.'
            )

        return value


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for reading messages.
    """

    conversation_title = serializers.CharField(source='conversation.title', read_only=True)
    owner = serializers.IntegerField(source='owner_id', read_only=True)
    attachments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Message
        fields = (
            'id',
            'conversation',
            'conversation_title',
            'owner',
            'role',
            'content',
            'is_edited',
            'is_deleted',
            'attachments_count',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'conversation',
            'conversation_title',
            'owner',
            'role',
            'is_edited',
            'is_deleted',
            'attachments_count',
            'created_at',
            'updated_at',
        )


class MessageCreateSerializer(serializers.Serializer):
    """
    Serializer for sending a new user message to a conversation.
    """

    content = serializers.CharField()

    def validate_content(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError('Message content cannot be empty.')

        return value


class MessageUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for editing a user message.
    """

    class Meta:
        model = Message
        fields = (
            'id',
            'content',
            'is_edited',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'is_edited',
            'updated_at',
        )

    def validate_content(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError('Message content cannot be empty.')

        return value

    def validate(self, attrs):
        if self.instance is not None and self.instance.role != Message.Role.USER:
            raise serializers.ValidationError(
                'Only user messages can be edited.'
            )

        return attrs

    def update(self, instance, validated_data):
        instance.content = validated_data.get('content', instance.content).strip()
        instance.is_edited = True
        instance.save(update_fields=['content', 'is_edited', 'updated_at'])
        return instance


class SendMessageResponseSerializer(serializers.Serializer):
    """
    Response serializer for sending a message and receiving a mock AI response.
    """

    message = serializers.CharField()
    user_message = MessageSerializer()
    assistant_message = MessageSerializer()