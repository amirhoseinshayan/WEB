from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import AIModel, Assistant, Conversation, Project


User = get_user_model()


class Phase4CrudApiTests(TestCase):
    """
    Tests for Phase 4 CRUD APIs and data isolation.
    """

    def setUp(self):
        self.client = APIClient()

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

        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='StrongPass123!',
        )

        self.free_model = AIModel.objects.create(
            name='GPT-3.5',
            provider='OpenAI',
            description='Free model',
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

        self.public_assistant = Assistant.objects.create(
            owner=None,
            title='Public Translator',
            description='Public assistant',
            system_prompt='You are a translator.',
            is_public=True,
        )

        self.user1_assistant = Assistant.objects.create(
            owner=self.user1,
            title='User 1 Private Assistant',
            description='Private assistant',
            system_prompt='You help user1.',
            is_public=False,
        )

        self.user2_assistant = Assistant.objects.create(
            owner=self.user2,
            title='User 2 Private Assistant',
            description='Private assistant',
            system_prompt='You help user2.',
            is_public=False,
        )

        self.conversation1 = Conversation.objects.create(
            owner=self.user1,
            project=self.project1,
            ai_model=self.free_model,
            assistant=self.user1_assistant,
            title='User 1 Conversation',
        )

    def get_results(self, response):
        if isinstance(response.data, dict) and 'results' in response.data:
            return response.data['results']

        return response.data

    def test_project_list_returns_only_current_user_projects(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.get('/api/projects/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = self.get_results(response)
        project_ids = [item['id'] for item in results]

        self.assertIn(self.project1.id, project_ids)
        self.assertNotIn(self.project2.id, project_ids)

    def test_project_create_sets_owner_automatically(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.post(
            '/api/projects/',
            {
                'title': 'New Project',
                'description': 'Created through API',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        project = Project.objects.get(id=response.data['id'])

        self.assertEqual(project.owner, self.user1)
        self.assertEqual(project.title, 'New Project')

    def test_user_cannot_retrieve_other_user_project(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(f'/api/projects/{self.project2.id}/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_authenticated_user_can_list_active_ai_models(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.get('/api/models/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = self.get_results(response)
        model_ids = [item['id'] for item in results]

        self.assertIn(self.free_model.id, model_ids)
        self.assertIn(self.premium_model.id, model_ids)

    def test_normal_user_cannot_create_ai_model(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.post(
            '/api/models/',
            {
                'name': 'Claude 3',
                'provider': 'Anthropic',
                'description': 'Another model',
                'is_active': True,
                'is_premium': False,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_ai_model(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            '/api/models/',
            {
                'name': 'Claude 3',
                'provider': 'Anthropic',
                'description': 'Another model',
                'is_active': True,
                'is_premium': False,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(AIModel.objects.filter(name='Claude 3').exists())

    def test_assistant_list_returns_public_and_owned_private_assistants(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.get('/api/assistants/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = self.get_results(response)
        assistant_ids = [item['id'] for item in results]

        self.assertIn(self.public_assistant.id, assistant_ids)
        self.assertIn(self.user1_assistant.id, assistant_ids)
        self.assertNotIn(self.user2_assistant.id, assistant_ids)

    def test_normal_user_cannot_create_public_assistant(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.post(
            '/api/assistants/',
            {
                'title': 'Public Assistant',
                'description': 'Should be rejected',
                'system_prompt': 'You are public.',
                'is_public': True,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_create_private_assistant(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.post(
            '/api/assistants/',
            {
                'title': 'Private Helper',
                'description': 'Private assistant',
                'system_prompt': 'You help privately.',
                'is_public': False,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        assistant = Assistant.objects.get(id=response.data['id'])

        self.assertEqual(assistant.owner, self.user1)
        self.assertFalse(assistant.is_public)

    def test_conversation_create_with_own_project_succeeds(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.post(
            '/api/conversations/',
            {
                'project': self.project1.id,
                'ai_model': self.free_model.id,
                'assistant': self.user1_assistant.id,
                'title': 'New Conversation',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        conversation = Conversation.objects.get(id=response.data['id'])

        self.assertEqual(conversation.owner, self.user1)
        self.assertEqual(conversation.project, self.project1)

    def test_conversation_create_with_other_user_project_fails(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.post(
            '/api/conversations/',
            {
                'project': self.project2.id,
                'ai_model': self.free_model.id,
                'title': 'Invalid Conversation',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_conversation_delete_is_soft_delete(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.delete(f'/api/conversations/{self.conversation1.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.conversation1.refresh_from_db()

        self.assertEqual(self.conversation1.status, Conversation.Status.DELETED)

    def test_project_conversations_endpoint_returns_only_project_conversations(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(f'/api/projects/{self.project1.id}/conversations/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = self.get_results(response)
        conversation_ids = [item['id'] for item in results]

        self.assertIn(self.conversation1.id, conversation_ids)