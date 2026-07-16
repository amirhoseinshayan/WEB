import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from .models import AIModel, Attachment, Conversation, Message, Project


User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class Phase10AttachmentApiTests(TestCase):
    """
    Tests for Phase 10 message attachments.
    """

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.client = APIClient()

        self.free_user = User.objects.create_user(
            username='phase10_free_user',
            email='phase10_free@example.com',
            password='StrongPass123!',
        )

        self.premium_user = User.objects.create_user(
            username='phase10_premium_user',
            email='phase10_premium@example.com',
            password='StrongPass123!',
            subscription_type=User.SubscriptionType.PREMIUM,
            premium_until=None,
        )

        self.other_user = User.objects.create_user(
            username='phase10_other_user',
            email='phase10_other@example.com',
            password='StrongPass123!',
        )

        self.ai_model = AIModel.objects.create(
            name='GPT-3.5',
            provider='OpenAI',
            description='Free model',
            is_active=True,
            is_premium=False,
        )

        self.premium_project = Project.objects.create(
            owner=self.premium_user,
            title='Premium Project',
            description='Project for premium user',
        )

        self.other_project = Project.objects.create(
            owner=self.other_user,
            title='Other Project',
            description='Project for other user',
        )

        self.premium_conversation = Conversation.objects.create(
            owner=self.premium_user,
            project=self.premium_project,
            ai_model=self.ai_model,
            title='Premium Conversation',
        )

        self.other_conversation = Conversation.objects.create(
            owner=self.other_user,
            project=self.other_project,
            ai_model=self.ai_model,
            title='Other Conversation',
        )

        self.user_message = Message.objects.create(
            conversation=self.premium_conversation,
            role=Message.Role.USER,
            content='Message with attachment',
        )

        self.assistant_message = Message.objects.create(
            conversation=self.premium_conversation,
            role=Message.Role.ASSISTANT,
            content='Assistant message',
        )

        self.other_user_message = Message.objects.create(
            conversation=self.other_conversation,
            role=Message.Role.USER,
            content='Other user message',
        )

    def get_results(self, response):
        if isinstance(response.data, dict) and 'results' in response.data:
            return response.data['results']

        return response.data

    def make_text_file(self, name='sample.txt', content=b'hello world'):
        return SimpleUploadedFile(
            name=name,
            content=content,
            content_type='text/plain',
        )

    def test_premium_user_can_upload_attachment_to_own_user_message(self):
        self.client.force_authenticate(user=self.premium_user)

        uploaded_file = self.make_text_file()

        response = self.client.post(
            f'/api/messages/{self.user_message.id}/attachments/',
            {
                'file': uploaded_file,
            },
            format='multipart',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['file_name'], 'sample.txt')
        self.assertEqual(response.data['file_format'], 'txt')
        self.assertGreater(response.data['file_size'], 0)

        self.assertTrue(
            Attachment.objects.filter(
                message=self.user_message,
                file_format='txt',
            ).exists()
        )

    def test_free_user_cannot_upload_attachment(self):
        free_project = Project.objects.create(
            owner=self.free_user,
            title='Free Project',
            description='Project for free user',
        )

        free_conversation = Conversation.objects.create(
            owner=self.free_user,
            project=free_project,
            ai_model=self.ai_model,
            title='Free Conversation',
        )

        free_message = Message.objects.create(
            conversation=free_conversation,
            role=Message.Role.USER,
            content='Free user message',
        )

        self.client.force_authenticate(user=self.free_user)

        response = self.client.post(
            f'/api/messages/{free_message.id}/attachments/',
            {
                'file': self.make_text_file(),
            },
            format='multipart',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_upload_attachment_to_other_user_message(self):
        self.client.force_authenticate(user=self.premium_user)

        response = self.client.post(
            f'/api/messages/{self.other_user_message.id}/attachments/',
            {
                'file': self.make_text_file(),
            },
            format='multipart',
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_cannot_upload_attachment_to_assistant_message(self):
        self.client.force_authenticate(user=self.premium_user)

        response = self.client.post(
            f'/api/messages/{self.assistant_message.id}/attachments/',
            {
                'file': self.make_text_file(),
            },
            format='multipart',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_file_extension_is_rejected(self):
        self.client.force_authenticate(user=self.premium_user)

        uploaded_file = SimpleUploadedFile(
            name='virus.exe',
            content=b'not allowed',
            content_type='application/octet-stream',
        )

        response = self.client.post(
            f'/api/messages/{self.user_message.id}/attachments/',
            {
                'file': uploaded_file,
            },
            format='multipart',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_oversized_file_is_rejected(self):
        self.client.force_authenticate(user=self.premium_user)

        large_file = SimpleUploadedFile(
            name='large.txt',
            content=b'a' * ((5 * 1024 * 1024) + 1),
            content_type='text/plain',
        )

        response = self.client.post(
            f'/api/messages/{self.user_message.id}/attachments/',
            {
                'file': large_file,
            },
            format='multipart',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_message_attachments(self):
        attachment = Attachment.objects.create(
            message=self.user_message,
            file=self.make_text_file(name='list-test.txt'),
        )

        self.client.force_authenticate(user=self.premium_user)

        response = self.client.get(
            f'/api/messages/{self.user_message.id}/attachments/'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = self.get_results(response)
        attachment_ids = [item['id'] for item in results]

        self.assertIn(attachment.id, attachment_ids)

    def test_user_can_list_only_own_attachments(self):
        own_attachment = Attachment.objects.create(
            message=self.user_message,
            file=self.make_text_file(name='own.txt'),
        )

        other_attachment = Attachment.objects.create(
            message=self.other_user_message,
            file=self.make_text_file(name='other.txt'),
        )

        self.client.force_authenticate(user=self.premium_user)

        response = self.client.get('/api/attachments/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = self.get_results(response)
        attachment_ids = [item['id'] for item in results]

        self.assertIn(own_attachment.id, attachment_ids)
        self.assertNotIn(other_attachment.id, attachment_ids)

    def test_user_can_retrieve_own_attachment(self):
        attachment = Attachment.objects.create(
            message=self.user_message,
            file=self.make_text_file(name='retrieve.txt'),
        )

        self.client.force_authenticate(user=self.premium_user)

        response = self.client.get(f'/api/attachments/{attachment.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], attachment.id)
        self.assertEqual(response.data['file_name'], 'retrieve.txt')

    def test_user_cannot_retrieve_other_user_attachment(self):
        attachment = Attachment.objects.create(
            message=self.other_user_message,
            file=self.make_text_file(name='private.txt'),
        )

        self.client.force_authenticate(user=self.premium_user)

        response = self.client.get(f'/api/attachments/{attachment.id}/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_delete_own_attachment(self):
        attachment = Attachment.objects.create(
            message=self.user_message,
            file=self.make_text_file(name='delete.txt'),
        )

        self.client.force_authenticate(user=self.premium_user)

        response = self.client.delete(f'/api/attachments/{attachment.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Attachment.objects.filter(id=attachment.id).exists())