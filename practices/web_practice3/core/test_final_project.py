from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from chats.models import AIModel, Conversation, Message, Project
from subscriptions.models import SubscriptionPlan


User = get_user_model()


class FinalProjectIntegrationTests(TestCase):
    """
    Final integration tests for the Web Practice 3 backend.

    These tests verify that the main user flow works from authentication
    to conversations, messages, subscriptions, and linked account switching.
    """

    def setUp(self):
        call_command('seed_initial_data', verbosity=0)
        self.client = APIClient()

    def get_results(self, response):
        if isinstance(response.data, dict) and 'results' in response.data:
            return response.data['results']

        return response.data

    def register_user(self, username, email, password='StrongPass123!'):
        return self.client.post(
            '/api/auth/register/',
            {
                'username': username,
                'email': email,
                'first_name': 'Final',
                'last_name': 'User',
                'password': password,
                'password_confirm': password,
            },
            format='json',
        )

    def login_user(self, identifier, password='StrongPass123!'):
        return self.client.post(
            '/api/auth/login/',
            {
                'identifier': identifier,
                'password': password,
            },
            format='json',
        )

    def authenticate_with_access_token(self, access_token):
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )

    def test_health_and_schema_endpoints_are_available(self):
        health_response = self.client.get('/api/health/')
        schema_response = self.client.get('/api/schema/')

        self.assertEqual(health_response.status_code, status.HTTP_200_OK)
        self.assertEqual(schema_response.status_code, status.HTTP_200_OK)

    def test_complete_chat_flow_for_free_user(self):
        register_response = self.register_user(
            username='final_user',
            email='final_user@example.com',
        )

        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)

        login_response = self.login_user('final_user')

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        access_token = login_response.data['access']
        self.authenticate_with_access_token(access_token)

        subscription_response = self.client.get('/api/subscription/status/')

        self.assertEqual(subscription_response.status_code, status.HTTP_200_OK)
        self.assertEqual(subscription_response.data['subscription_type'], 'free')

        models_response = self.client.get('/api/models/')

        self.assertEqual(models_response.status_code, status.HTTP_200_OK)

        models = self.get_results(models_response)
        free_model = next(
            item for item in models
            if item['name'] == 'GPT-3.5'
        )

        project_response = self.client.post(
            '/api/projects/',
            {
                'title': 'Final Integration Project',
                'description': 'Project created by final integration test.',
            },
            format='json',
        )

        self.assertEqual(project_response.status_code, status.HTTP_201_CREATED)

        conversation_response = self.client.post(
            '/api/conversations/',
            {
                'project': project_response.data['id'],
                'ai_model': free_model['id'],
                'title': 'Final Integration Conversation',
            },
            format='json',
        )

        self.assertEqual(conversation_response.status_code, status.HTTP_201_CREATED)

        conversation_id = conversation_response.data['id']

        message_response = self.client.post(
            f'/api/conversations/{conversation_id}/messages/',
            {
                'content': 'Hello from the final integration test.',
            },
            format='json',
        )

        self.assertEqual(message_response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user_message', message_response.data)
        self.assertIn('assistant_message', message_response.data)

        self.assertEqual(
            message_response.data['user_message']['role'],
            Message.Role.USER,
        )

        self.assertEqual(
            message_response.data['assistant_message']['role'],
            Message.Role.ASSISTANT,
        )

        history_response = self.client.get(
            f'/api/conversations/{conversation_id}/messages/'
        )

        self.assertEqual(history_response.status_code, status.HTTP_200_OK)

        messages = self.get_results(history_response)

        self.assertGreaterEqual(len(messages), 2)

    def test_premium_purchase_enables_premium_model_conversation(self):
        user = User.objects.create_user(
            username='final_premium_user',
            email='final_premium_user@example.com',
            password='StrongPass123!',
        )

        self.client.force_authenticate(user=user)

        premium_plan = SubscriptionPlan.objects.filter(
            plan_type=SubscriptionPlan.PlanType.PREMIUM,
            is_active=True,
        ).order_by('price').first()

        self.assertIsNotNone(premium_plan)

        purchase_response = self.client.post(
            '/api/subscription/purchase/',
            {
                'plan_id': premium_plan.id,
            },
            format='json',
        )

        self.assertEqual(purchase_response.status_code, status.HTTP_200_OK)

        user.refresh_from_db()

        self.assertTrue(user.is_premium)

        premium_model = AIModel.objects.filter(
            is_premium=True,
            is_active=True,
        ).first()

        self.assertIsNotNone(premium_model)

        project = Project.objects.create(
            owner=user,
            title='Premium Final Project',
            description='Premium project for final test.',
        )

        conversation_response = self.client.post(
            '/api/conversations/',
            {
                'project': project.id,
                'ai_model': premium_model.id,
                'title': 'Premium Final Conversation',
            },
            format='json',
        )

        self.assertEqual(conversation_response.status_code, status.HTTP_201_CREATED)

        conversation = Conversation.objects.get(id=conversation_response.data['id'])

        self.assertEqual(conversation.ai_model, premium_model)

    def test_linked_account_switching_flow(self):
        main_user = User.objects.create_user(
            username='final_main_user',
            email='final_main_user@example.com',
            password='StrongPass123!',
        )

        linked_user = User.objects.create_user(
            username='final_linked_user',
            email='final_linked_user@example.com',
            password='StrongPass123!',
        )

        self.client.force_authenticate(user=main_user)

        link_response = self.client.post(
            '/api/linked-accounts/',
            {
                'identifier': 'final_linked_user',
            },
            format='json',
        )

        self.assertEqual(link_response.status_code, status.HTTP_201_CREATED)

        switch_response = self.client.post(
            '/api/auth/switch-account/',
            {
                'linked_user_id': linked_user.id,
            },
            format='json',
        )

        self.assertEqual(switch_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', switch_response.data)
        self.assertEqual(
            switch_response.data['switched_to']['id'],
            linked_user.id,
        )

        switched_client = APIClient()
        switched_client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {switch_response.data['access']}"
        )

        profile_response = switched_client.get('/api/auth/profile/')

        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_response.data['user']['id'], linked_user.id)
        