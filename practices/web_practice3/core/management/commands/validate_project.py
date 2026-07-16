from django.apps import apps
from django.conf import settings
from django.core.management import CommandError, call_command
from django.core.management.base import BaseCommand
from django.urls import Resolver404, resolve


class Command(BaseCommand):
    """
    Final validation command for Web Practice 3.

    This command checks:
    - Django system check
    - pending model migrations
    - required installed apps
    - required API routes
    - media/static/auth settings
    """

    help = 'Run final validation checks before delivering the project.'

    required_apps = [
        'rest_framework',
        'drf_spectacular',
        'accounts',
        'chats',
        'subscriptions',
        'core',
    ]

    required_routes = [
        '/api/health/',
        '/api/schema/',
        '/api/docs/',
        '/api/redoc/',

        '/api/auth/register/',
        '/api/auth/login/',
        '/api/auth/token/refresh/',
        '/api/auth/profile/',
        '/api/auth/switch-account/',

        '/api/linked-accounts/',
        '/api/subscription/status/',
        '/api/subscription/plans/',
        '/api/subscription/purchase/',

        '/api/projects/',
        '/api/models/',
        '/api/assistants/',
        '/api/assistants/public/',
        '/api/assistants/mine/',
        '/api/conversations/',
        '/api/messages/',
        '/api/attachments/',

        '/api/projects/1/conversations/',
        '/api/conversations/1/messages/',
        '/api/conversations/1/assistant/',
        '/api/messages/1/attachments/',
    ]

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting final project validation...'))

        self.run_system_check()
        self.check_pending_migrations()
        self.check_required_apps()
        self.check_settings()
        self.check_required_routes()

        self.stdout.write(
            self.style.SUCCESS(
                'Final validation completed successfully. Project is ready for delivery.'
            )
        )

    def run_system_check(self):
        self.stdout.write('Running Django system check...')

        call_command('check')

        self.stdout.write(
            self.style.SUCCESS('Django system check passed.')
        )

    def check_pending_migrations(self):
        self.stdout.write('Checking pending migrations...')

        try:
            call_command(
                'makemigrations',
                check=True,
                dry_run=True,
                verbosity=0,
            )
        except SystemExit as exc:
            raise CommandError(
                'Pending model changes detected. Run makemigrations before delivery.'
            ) from exc

        self.stdout.write(
            self.style.SUCCESS('No pending migrations detected.')
        )

    def check_required_apps(self):
        self.stdout.write('Checking required installed apps...')

        missing_apps = []

        for app_label in self.required_apps:
            try:
                apps.get_app_config(app_label.split('.')[-1])
            except LookupError:
                if app_label not in settings.INSTALLED_APPS:
                    missing_apps.append(app_label)

        if missing_apps:
            raise CommandError(
                f'Missing required apps: {", ".join(missing_apps)}'
            )

        self.stdout.write(
            self.style.SUCCESS('Required apps are installed.')
        )

    def check_settings(self):
        self.stdout.write('Checking important settings...')

        if settings.AUTH_USER_MODEL != 'accounts.User':
            raise CommandError(
                'AUTH_USER_MODEL must be accounts.User.'
            )

        if not hasattr(settings, 'MEDIA_URL') or not settings.MEDIA_URL:
            raise CommandError(
                'MEDIA_URL is not configured.'
            )

        if not hasattr(settings, 'MEDIA_ROOT') or not settings.MEDIA_ROOT:
            raise CommandError(
                'MEDIA_ROOT is not configured.'
            )

        if 'DEFAULT_SCHEMA_CLASS' not in settings.REST_FRAMEWORK:
            raise CommandError(
                'DEFAULT_SCHEMA_CLASS is not configured in REST_FRAMEWORK.'
            )

        self.stdout.write(
            self.style.SUCCESS('Important settings are valid.')
        )

    def check_required_routes(self):
        self.stdout.write('Checking required API routes...')

        missing_routes = []

        for route in self.required_routes:
            try:
                resolve(route)
            except Resolver404:
                missing_routes.append(route)

        if missing_routes:
            raise CommandError(
                'Missing required routes:\n' + '\n'.join(missing_routes)
            )

        self.stdout.write(
            self.style.SUCCESS('Required API routes are available.')
        )