from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import AIModel, Assistant, Conversation, Message, Project


User = get_user_model()


class Phase7MessageApiTests(TestCase):
    """
    Tests for Phase 7 conversation messages and mock AI responses.
    """

    def setUp(self):
        self.client = APIClient()

        self.user1 = User.objects.create_user(
            username='phase7_user1',
            email='phase7_user1@example.com',
            password='StrongPass123!',
        )

        self.user2 = User.objects.create_user(
            username='phase7_user2',
            email='phase7_user2@example.com',
            password='StrongPass123!',
        )

        self.ai_model = AIModel.objects.create(
            name='GPT-3.5',
            provider='OpenAI',
            description='Free model',
            is_active=True,
            is_premium=False,
        )

        self.project1 = Project.objects.create(
            owner=self.user1,
            title='Phase 7 Project 1',
            description='Project for user1',
        )

        self.project2 = Project.objects.create(
            owner=self.user2,
            title='Phase 7 Project 2',
            description='Project for user2',
        )

        self.assistant1 = Assistant.objects.create(
            owner=self.user1,
            title='Phase 7 Assistant',
            description='Private assistant',
            system_prompt='You help user1.',
            is_public=False,
        )

        self.conversation1 = Conversation.objects.create(
            owner=self.user1,
            project=self.project1,
            ai_model=self.ai_model,
            assistant=self.assistant1,
            title='Phase 7 Conversation 1',
        )

        self.conversation2 = Conversation.objects.create(
            owner=self.user2,
            project=self.project2,
            ai_model=self.ai_model,
            assistant=None,
            title='Phase 7 Conversation 2',
        )

        self.user_message = Message.objects.create(
            conversation=self.conversation1,
            role=Message.Role.USER,
            content='Initial user message',
        )

        self.assistant_message = Message.objects.create(
            conversation=self.conversation1,
            role=Message.Role.ASSISTANT,
            content='Initial assistant response',
        )

    def get_results(self, response):
        if isinstance(response.data, dict) and 'results' in response.data:
            return response.data['results']

        return response.data

    def test_conversation_messages_list_returns_only_conversation_messages(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(
            f'/api/conversations/{self.conversation1.id}/messages/'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = self.get_results(response)
        message_ids = [item['id'] for item in results]

        self.assertIn(self.user_message.id, message_ids)
        self.assertIn(self.assistant_message.id, message_ids)

    def test_user_cannot_list_messages_of_other_user_conversation(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(
            f'/api/conversations/{self.conversation2.id}/messages/'
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_send_message_creates_user_and_assistant_messages(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.post(
            f'/api/conversations/{self.conversation1.id}/messages/',
            {
                'content': 'Explain Django serializers.',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertIn('user_message', response.data)
        self.assertIn('assistant_message', response.data)

        self.assertEqual(response.data['user_message']['role'], Message.Role.USER)
        self.assertEqual(response.data['assistant_message']['role'], Message.Role.ASSISTANT)

        self.assertTrue(
            Message.objects.filter(
                conversation=self.conversation1,
                role=Message.Role.USER,
                content='Explain Django serializers.',
            ).exists()
        )

        self.assertTrue(
            Message.objects.filter(
                conversation=self.conversation1,
                role=Message.Role.ASSISTANT,
            ).exists()
        )

    def test_mock_response_contains_model_and_assistant_information(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.post(
            f'/api/conversations/{self.conversation1.id}/messages/',
            {
                'content': 'Hello model.',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        assistant_content = response.data['assistant_message']['content']

        self.assertIn('OpenAI', assistant_content)
        self.assertIn('GPT-3.5', assistant_content)
        self.assertIn('Phase 7 Assistant', assistant_content)

    def test_empty_message_is_rejected(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.post(
            f'/api/conversations/{self.conversation1.id}/messages/',
            {
                'content': '   ',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_edit_own_user_message(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.patch(
            f'/api/messages/{self.user_message.id}/',
            {
                'content': 'Edited user message',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user_message.refresh_from_db()

        self.assertEqual(self.user_message.content, 'Edited user message')
        self.assertTrue(self.user_message.is_edited)

    def test_user_cannot_edit_assistant_message(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.patch(
            f'/api/messages/{self.assistant_message.id}/',
            {
                'content': 'Trying to edit assistant message',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_soft_delete_own_message(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.delete(
            f'/api/messages/{self.user_message.id}/'
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.user_message.refresh_from_db()

        self.assertTrue(self.user_message.is_deleted)

    def test_user_cannot_access_other_user_message(self):
        other_message = Message.objects.create(
            conversation=self.conversation2,
            role=Message.Role.USER,
            content='Other user message',
        )

        self.client.force_authenticate(user=self.user1)

        response = self.client.get(
            f'/api/messages/{other_message.id}/'
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)