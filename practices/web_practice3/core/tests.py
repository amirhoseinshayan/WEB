from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from chats.models import AIModel, Assistant, Attachment, Conversation, Message, Project


User = get_user_model()


class Phase3DataIsolationTests(TestCase):
    """
    Tests for Phase 3 data isolation helper methods.

    These tests verify the ownership and availability logic that will be used
    later by API ViewSets and permissions.
    """

    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='StrongPass123!',
        )

        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='StrongPass123!',
        )

        self.free_model = AIModel.objects.create(
            name='GPT-3.5',
            provider='OpenAI',
            description='Basic free model',
            is_active=True,
            is_premium=False,
        )

        self.premium_model = AIModel.objects.create(
            name='GPT-4',
            provider='OpenAI',
            description='Premium model',
            is_active=True,
            is_premium=True,
        )

        self.project1 = Project.objects.create(
            owner=self.user1,
            title='User 1 Project',
            description='Project owned by user1',
        )

        self.project2 = Project.objects.create(
            owner=self.user2,
            title='User 2 Project',
            description='Project owned by user2',
        )

        self.private_assistant = Assistant.objects.create(
            owner=self.user1,
            title='Private Coding Assistant',
            description='Private assistant for user1',
            system_prompt='You are a coding assistant.',
            is_public=False,
        )

        self.public_assistant = Assistant.objects.create(
            owner=None,
            title='Public Translator',
            description='Public assistant for all users',
            system_prompt='You are a translator.',
            is_public=True,
        )

        self.conversation = Conversation.objects.create(
            owner=self.user1,
            project=self.project1,
            ai_model=self.free_model,
            assistant=self.private_assistant,
            title='User 1 Conversation',
        )

        self.message = Message.objects.create(
            conversation=self.conversation,
            role=Message.Role.USER,
            content='Hello',
        )

    def test_project_is_owned_only_by_its_owner(self):
        self.assertTrue(self.project1.is_owned_by(self.user1))
        self.assertFalse(self.project1.is_owned_by(self.user2))

    def test_private_assistant_is_available_only_to_owner(self):
        self.assertTrue(self.private_assistant.is_available_to(self.user1))
        self.assertFalse(self.private_assistant.is_available_to(self.user2))

    def test_public_assistant_is_available_to_authenticated_users(self):
        self.assertTrue(self.public_assistant.is_available_to(self.user1))
        self.assertTrue(self.public_assistant.is_available_to(self.user2))

    def test_free_ai_model_is_available_to_free_user(self):
        self.assertTrue(self.free_model.is_available_to(self.user1))

    def test_premium_ai_model_is_not_available_to_free_user(self):
        self.assertFalse(self.premium_model.is_available_to(self.user1))

    def test_conversation_cannot_use_project_from_another_user(self):
        invalid_conversation = Conversation(
            owner=self.user1,
            project=self.project2,
            ai_model=self.free_model,
            title='Invalid Conversation',
        )

        with self.assertRaises(ValidationError):
            invalid_conversation.full_clean()

    def test_message_owner_is_conversation_owner(self):
        self.assertEqual(self.message.owner_id, self.user1.id)
        self.assertTrue(self.message.is_owned_by(self.user1))
        self.assertFalse(self.message.is_owned_by(self.user2))

    def test_attachment_owner_is_message_conversation_owner(self):
        uploaded_file = SimpleUploadedFile(
            name='test.txt',
            content=b'hello world',
            content_type='text/plain',
        )

        attachment = Attachment.objects.create(
            message=self.message,
            file=uploaded_file,
        )

        self.assertEqual(attachment.owner_id, self.user1.id)
        self.assertTrue(attachment.is_owned_by(self.user1))
        self.assertFalse(attachment.is_owned_by(self.user2))
        self.assertEqual(attachment.file_format, 'txt')
        self.assertGreater(attachment.file_size, 0)