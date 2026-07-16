from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from chats.models import AIModel, Conversation, Message, Project
from subscriptions.models import SubscriptionPlan


User = get_user_model()


class Phase8SubscriptionApiTests(TestCase):
    """
    Tests for Phase 8 subscription APIs and Free user limits.
    """

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username='phase8_user',
            email='phase8_user@example.com',
            password='StrongPass123!',
        )

        self.free_plan = SubscriptionPlan.objects.create(
            name='Free Plan',
            plan_type=SubscriptionPlan.PlanType.FREE,
            description='Free plan for tests',
            price='0.00',
            duration_days=0,
            daily_message_limit=2,
            can_use_premium_models=False,
            can_upload_files=False,
            is_active=True,
        )

        self.premium_plan = SubscriptionPlan.objects.create(
            name='Premium Monthly',
            plan_type=SubscriptionPlan.PlanType.PREMIUM,
            description='Premium plan for tests',
            price='9.99',
            duration_days=30,
            daily_message_limit=None,
            can_use_premium_models=True,
            can_upload_files=True,
            is_active=True,
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

        self.project = Project.objects.create(
            owner=self.user,
            title='Phase 8 Project',
            description='Project for subscription tests',
        )

        self.conversation = Conversation.objects.create(
            owner=self.user,
            project=self.project,
            ai_model=self.free_model,
            assistant=None,
            title='Phase 8 Conversation',
        )

    def get_results(self, response):
        if isinstance(response.data, dict) and 'results' in response.data:
            return response.data['results']

        return response.data

    def test_subscription_status_for_free_user(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/subscription/status/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['subscription_type'], 'free')
        self.assertFalse(response.data['is_premium'])
        self.assertEqual(response.data['daily_message_limit'], 2)
        self.assertEqual(response.data['daily_messages_used'], 0)
        self.assertEqual(response.data['daily_messages_remaining'], 2)
        self.assertFalse(response.data['can_use_premium_models'])

    def test_subscription_plans_endpoint_returns_active_plans(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/subscription/plans/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = self.get_results(response)
        plan_names = [item['name'] for item in results]

        self.assertIn('Free Plan', plan_names)
        self.assertIn('Premium Monthly', plan_names)

    def test_purchase_premium_plan_upgrades_user(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            '/api/subscription/purchase/',
            {
                'plan_id': self.premium_plan.id,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()

        self.assertEqual(self.user.subscription_type, User.SubscriptionType.PREMIUM)
        self.assertTrue(self.user.is_premium)
        self.assertIsNotNone(self.user.premium_until)
        self.assertTrue(response.data['subscription_status']['can_use_premium_models'])

    def test_purchase_free_plan_downgrades_user(self):
        self.user.subscription_type = User.SubscriptionType.PREMIUM
        self.user.premium_until = None
        self.user.save(update_fields=['subscription_type', 'premium_until', 'updated_at'])

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            '/api/subscription/purchase/',
            {
                'plan_id': self.free_plan.id,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()

        self.assertEqual(self.user.subscription_type, User.SubscriptionType.FREE)
        self.assertFalse(self.user.is_premium)
        self.assertIsNone(self.user.premium_until)

    def test_free_user_daily_message_limit_is_enforced(self):
        self.client.force_authenticate(user=self.user)

        first_response = self.client.post(
            f'/api/conversations/{self.conversation.id}/messages/',
            {
                'content': 'First message',
            },
            format='json',
        )

        second_response = self.client.post(
            f'/api/conversations/{self.conversation.id}/messages/',
            {
                'content': 'Second message',
            },
            format='json',
        )

        third_response = self.client.post(
            f'/api/conversations/{self.conversation.id}/messages/',
            {
                'content': 'Third message should be blocked',
            },
            format='json',
        )

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(third_response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        user_message_count = Message.objects.filter(
            conversation__owner=self.user,
            role=Message.Role.USER,
        ).count()

        self.assertEqual(user_message_count, 2)

    def test_premium_user_has_unlimited_daily_messages(self):
        self.user.subscription_type = User.SubscriptionType.PREMIUM
        self.user.premium_until = None
        self.user.save(update_fields=['subscription_type', 'premium_until', 'updated_at'])

        self.client.force_authenticate(user=self.user)

        for index in range(5):
            response = self.client.post(
                f'/api/conversations/{self.conversation.id}/messages/',
                {
                    'content': f'Premium message {index + 1}',
                },
                format='json',
            )

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user_message_count = Message.objects.filter(
            conversation__owner=self.user,
            role=Message.Role.USER,
        ).count()

        self.assertEqual(user_message_count, 5)

    def test_free_user_cannot_create_conversation_with_premium_model(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            '/api/conversations/',
            {
                'project': self.project.id,
                'ai_model': self.premium_model.id,
                'title': 'Premium model conversation',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_premium_user_can_create_conversation_with_premium_model(self):
        self.user.subscription_type = User.SubscriptionType.PREMIUM
        self.user.premium_until = None
        self.user.save(update_fields=['subscription_type', 'premium_until', 'updated_at'])

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            '/api/conversations/',
            {
                'project': self.project.id,
                'ai_model': self.premium_model.id,
                'title': 'Premium model conversation',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        conversation = Conversation.objects.get(id=response.data['id'])

        self.assertEqual(conversation.ai_model, self.premium_model)