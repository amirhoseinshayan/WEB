from django.contrib import admin

from .models import AIModel, Assistant, Attachment, Conversation, Message, Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'owner',
        'created_at',
        'updated_at',
    )

    list_filter = (
        'created_at',
        'updated_at',
    )

    search_fields = (
        'title',
        'description',
        'owner__username',
        'owner__email',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    ordering = ('-created_at',)


@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'provider',
        'is_active',
        'is_premium',
        'created_at',
    )

    list_filter = (
        'provider',
        'is_active',
        'is_premium',
    )

    search_fields = (
        'name',
        'provider',
        'description',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    ordering = (
        'provider',
        'name',
    )


@admin.register(Assistant)
class AssistantAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'owner',
        'is_public',
        'created_at',
    )

    list_filter = (
        'is_public',
        'created_at',
    )

    search_fields = (
        'title',
        'description',
        'system_prompt',
        'owner__username',
        'owner__email',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    ordering = ('-created_at',)


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'owner',
        'project',
        'ai_model',
        'assistant',
        'status',
        'created_at',
    )

    list_filter = (
        'status',
        'ai_model',
        'created_at',
    )

    search_fields = (
        'title',
        'owner__username',
        'owner__email',
        'project__title',
        'ai_model__name',
        'assistant__title',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    ordering = ('-created_at',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'conversation',
        'role',
        'is_edited',
        'is_deleted',
        'created_at',
    )

    list_filter = (
        'role',
        'is_edited',
        'is_deleted',
        'created_at',
    )

    search_fields = (
        'content',
        'conversation__title',
        'conversation__owner__username',
        'conversation__owner__email',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    ordering = ('-created_at',)


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'message',
        'file_name',
        'file_format',
        'file_size',
        'uploaded_at',
    )

    list_filter = (
        'file_format',
        'uploaded_at',
    )

    search_fields = (
        'file',
        'message__content',
        'message__conversation__title',
    )

    readonly_fields = (
        'uploaded_at',
        'file_size',
        'file_format',
    )

    ordering = ('-uploaded_at',)