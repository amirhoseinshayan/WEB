from decimal import Decimal

from django.core.management.base import BaseCommand

from chats.models import AIModel, Assistant
from subscriptions.models import SubscriptionPlan


class Command(BaseCommand):
    """
    Seed initial data for the ChatGPT-like backend.

    This command creates:
    - default AI models
    - default public assistants
    - default subscription plans

    The command is idempotent, meaning it can be executed multiple times
    without creating duplicate records.
    """

    help = 'Seed initial AI models, public assistants, and subscription plans.'

    def handle(self, *args, **options):
        self.stdout.write('Seeding initial data...')

        ai_created, ai_updated = self.seed_ai_models()
        assistants_created, assistants_updated = self.seed_public_assistants()
        plans_created, plans_updated = self.seed_subscription_plans()

        self.stdout.write(
            self.style.SUCCESS(
                'Initial data seeding completed successfully.'
            )
        )

        self.stdout.write(
            f'AI Models: {ai_created} created, {ai_updated} updated.'
        )

        self.stdout.write(
            f'Public Assistants: {assistants_created} created, {assistants_updated} updated.'
        )

        self.stdout.write(
            f'Subscription Plans: {plans_created} created, {plans_updated} updated.'
        )

    def seed_ai_models(self):
        """
        Create or update default AI models.
        """

        ai_models = [
            {
                'name': 'GPT-3.5',
                'provider': 'OpenAI',
                'defaults': {
                    'description': 'Basic free model for regular users.',
                    'is_active': True,
                    'is_premium': False,
                },
            },
            {
                'name': 'GPT-4',
                'provider': 'OpenAI',
                'defaults': {
                    'description': 'Premium model with stronger reasoning capabilities.',
                    'is_active': True,
                    'is_premium': True,
                },
            },
            {
                'name': 'Claude-3',
                'provider': 'Anthropic',
                'defaults': {
                    'description': 'Premium assistant model by Anthropic.',
                    'is_active': True,
                    'is_premium': True,
                },
            },
            {
                'name': 'Llama-3',
                'provider': 'Meta',
                'defaults': {
                    'description': 'Open-weight style model available for free users.',
                    'is_active': True,
                    'is_premium': False,
                },
            },
        ]

        created_count = 0
        updated_count = 0

        for item in ai_models:
            _, created = AIModel.objects.update_or_create(
                name=item['name'],
                provider=item['provider'],
                defaults=item['defaults'],
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        return created_count, updated_count

    def seed_public_assistants(self):
        """
        Create or update default public assistants.

        Public assistants have no owner and can be used by all authenticated users.
        """

        assistants = [
            {
                'title': 'General Assistant',
                'defaults': {
                    'owner': None,
                    'description': 'A helpful general-purpose assistant.',
                    'system_prompt': 'You are a helpful, accurate, and concise AI assistant.',
                    'is_public': True,
                },
            },
            {
                'title': 'Coding Assistant',
                'defaults': {
                    'owner': None,
                    'description': 'A public assistant for programming and debugging tasks.',
                    'system_prompt': 'You are an expert programming assistant. Explain code clearly and help debug problems step by step.',
                    'is_public': True,
                },
            },
            {
                'title': 'Translator Assistant',
                'defaults': {
                    'owner': None,
                    'description': 'A public assistant for translation tasks.',
                    'system_prompt': 'You are a professional translator. Translate accurately while preserving meaning and tone.',
                    'is_public': True,
                },
            },
            {
                'title': 'Academic Writing Assistant',
                'defaults': {
                    'owner': None,
                    'description': 'A public assistant for academic writing and editing.',
                    'system_prompt': 'You help users write, edit, and improve academic text in a clear and structured way.',
                    'is_public': True,
                },
            },
            {
                'title': 'Literary Critic',
                'defaults': {
                    'owner': None,
                    'description': 'A public assistant for reviewing and analyzing literature.',
                    'system_prompt': 'You are a literary critic. Analyze texts carefully and provide thoughtful feedback.',
                    'is_public': True,
                },
            },
        ]

        created_count = 0
        updated_count = 0

        for item in assistants:
            _, created = Assistant.objects.update_or_create(
                title=item['title'],
                is_public=True,
                defaults=item['defaults'],
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        return created_count, updated_count

    def seed_subscription_plans(self):
        """
        Create or update default subscription plans.
        """

        plans = [
            {
                'name': 'Free Plan',
                'defaults': {
                    'plan_type': SubscriptionPlan.PlanType.FREE,
                    'description': 'Default free plan with limited daily messages and access to basic models.',
                    'price': Decimal('0.00'),
                    'duration_days': 0,
                    'daily_message_limit': 50,
                    'can_use_premium_models': False,
                    'can_upload_files': False,
                    'is_active': True,
                },
            },
            {
                'name': 'Premium Monthly',
                'defaults': {
                    'plan_type': SubscriptionPlan.PlanType.PREMIUM,
                    'description': 'Monthly premium plan with access to premium models and file uploads.',
                    'price': Decimal('9.99'),
                    'duration_days': 30,
                    'daily_message_limit': None,
                    'can_use_premium_models': True,
                    'can_upload_files': True,
                    'is_active': True,
                },
            },
            {
                'name': 'Premium Yearly',
                'defaults': {
                    'plan_type': SubscriptionPlan.PlanType.PREMIUM,
                    'description': 'Yearly premium plan with access to all premium features.',
                    'price': Decimal('99.99'),
                    'duration_days': 365,
                    'daily_message_limit': None,
                    'can_use_premium_models': True,
                    'can_upload_files': True,
                    'is_active': True,
                },
            },
        ]

        created_count = 0
        updated_count = 0

        for item in plans:
            _, created = SubscriptionPlan.objects.update_or_create(
                name=item['name'],
                defaults=item['defaults'],
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        return created_count, updated_count