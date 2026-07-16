from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from chats.models import AIModel, Assistant
from subscriptions.models import SubscriptionPlan


User = get_user_model()


class SeedInitialDataCommandTests(TestCase):
    """
    Tests for the seed_initial_data management command.
    """

    def test_seed_initial_data_creates_ai_models_assistants_and_plans(self):
        call_command('seed_initial_data', verbosity=0)

        self.assertTrue(
            AIModel.objects.filter(
                name='GPT-3.5',
                provider='OpenAI',
                is_active=True,
                is_premium=False,
            ).exists()
        )

        self.assertTrue(
            AIModel.objects.filter(
                name='GPT-4',
                provider='OpenAI',
                is_active=True,
                is_premium=True,
            ).exists()
        )

        self.assertTrue(
            AIModel.objects.filter(
                name='Claude-3',
                provider='Anthropic',
                is_active=True,
                is_premium=True,
            ).exists()
        )

        self.assertTrue(
            Assistant.objects.filter(
                title='General Assistant',
                is_public=True,
                owner__isnull=True,
            ).exists()
        )

        self.assertTrue(
            Assistant.objects.filter(
                title='Coding Assistant',
                is_public=True,
                owner__isnull=True,
            ).exists()
        )

        self.assertTrue(
            SubscriptionPlan.objects.filter(
                name='Free Plan',
                plan_type=SubscriptionPlan.PlanType.FREE,
                daily_message_limit=50,
                can_use_premium_models=False,
                can_upload_files=False,
            ).exists()
        )

        self.assertTrue(
            SubscriptionPlan.objects.filter(
                name='Premium Monthly',
                plan_type=SubscriptionPlan.PlanType.PREMIUM,
                daily_message_limit__isnull=True,
                can_use_premium_models=True,
                can_upload_files=True,
            ).exists()
        )

    def test_seed_initial_data_is_idempotent(self):
        call_command('seed_initial_data', verbosity=0)

        first_ai_model_count = AIModel.objects.count()
        first_assistant_count = Assistant.objects.count()
        first_plan_count = SubscriptionPlan.objects.count()

        call_command('seed_initial_data', verbosity=0)

        self.assertEqual(AIModel.objects.count(), first_ai_model_count)
        self.assertEqual(Assistant.objects.count(), first_assistant_count)
        self.assertEqual(SubscriptionPlan.objects.count(), first_plan_count)

    def test_ai_models_api_includes_availability_flag_for_free_user(self):
        call_command('seed_initial_data', verbosity=0)

        user = User.objects.create_user(
            username='freeuser',
            email='freeuser@example.com',
            password='StrongPass123!',
        )

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get('/api/models/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        if isinstance(response.data, dict) and 'results' in response.data:
            results = response.data['results']
        else:
            results = response.data

        self.assertGreaterEqual(len(results), 1)

        for item in results:
            self.assertIn('is_available_for_current_user', item)

        gpt_35 = next(item for item in results if item['name'] == 'GPT-3.5')
        gpt_4 = next(item for item in results if item['name'] == 'GPT-4')

        self.assertTrue(gpt_35['is_available_for_current_user'])
        self.assertFalse(gpt_4['is_available_for_current_user'])