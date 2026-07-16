from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import LinkedAccount


User = get_user_model()


class Phase9LinkedAccountTests(TestCase):
    """
    Tests for Phase 9 linked accounts and account switching.
    """

    def setUp(self):
        self.client = APIClient()

        self.user1 = User.objects.create_user(
            username='phase9_user1',
            email='phase9_user1@example.com',
            password='StrongPass123!',
            first_name='User',
            last_name='One',
        )

        self.user2 = User.objects.create_user(
            username='phase9_user2',
            email='phase9_user2@example.com',
            password='StrongPass123!',
            first_name='User',
            last_name='Two',
        )

        self.user3 = User.objects.create_user(
            username='phase9_user3',
            email='phase9_user3@example.com',
            password='StrongPass123!',
            first_name='User',
            last_name='Three',
        )

    def get_results(self, response):
        if isinstance(response.data, dict) and 'results' in response.data:
            return response.data['results']

        return response.data

    def test_user_can_link_another_account_by_username(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.post(
            '/api/linked-accounts/',
            {
                'identifier': 'phase9_user2',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Account linked successfully.')

        self.assertTrue(
            LinkedAccount.objects.filter(
                owner=self.user1,
                linked_user=self.user2,
                is_active=True,
            ).exists()
        )

    def test_user_can_link_another_account_by_email(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.post(
            '/api/linked-accounts/',
            {
                'identifier': 'phase9_user2@example.com',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        linked_account = LinkedAccount.objects.get(
            owner=self.user1,
            linked_user=self.user2,
        )

        self.assertTrue(linked_account.is_active)

    def test_user_cannot_link_account_to_itself(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.post(
            '/api/linked-accounts/',
            {
                'identifier': 'phase9_user1',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_cannot_create_duplicate_link(self):
        LinkedAccount.objects.create(
            owner=self.user1,
            linked_user=self.user2,
            is_active=True,
        )

        self.client.force_authenticate(user=self.user1)

        response = self.client.post(
            '/api/linked-accounts/',
            {
                'identifier': 'phase9_user2',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_linked_accounts_list_returns_only_current_user_links(self):
        link1 = LinkedAccount.objects.create(
            owner=self.user1,
            linked_user=self.user2,
            is_active=True,
        )

        link2 = LinkedAccount.objects.create(
            owner=self.user2,
            linked_user=self.user3,
            is_active=True,
        )

        self.client.force_authenticate(user=self.user1)

        response = self.client.get('/api/linked-accounts/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = self.get_results(response)
        linked_account_ids = [item['id'] for item in results]

        self.assertIn(link1.id, linked_account_ids)
        self.assertNotIn(link2.id, linked_account_ids)

    def test_user_can_retrieve_own_linked_account(self):
        linked_account = LinkedAccount.objects.create(
            owner=self.user1,
            linked_user=self.user2,
            is_active=True,
        )

        self.client.force_authenticate(user=self.user1)

        response = self.client.get(f'/api/linked-accounts/{linked_account.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['linked_user'], self.user2.id)
        self.assertEqual(response.data['linked_username'], self.user2.username)

    def test_user_cannot_retrieve_other_user_linked_account(self):
        linked_account = LinkedAccount.objects.create(
            owner=self.user2,
            linked_user=self.user3,
            is_active=True,
        )

        self.client.force_authenticate(user=self.user1)

        response = self.client.get(f'/api/linked-accounts/{linked_account.id}/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_delete_own_linked_account(self):
        linked_account = LinkedAccount.objects.create(
            owner=self.user1,
            linked_user=self.user2,
            is_active=True,
        )

        self.client.force_authenticate(user=self.user1)

        response = self.client.delete(f'/api/linked-accounts/{linked_account.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(
            LinkedAccount.objects.filter(id=linked_account.id).exists()
        )

    def test_user_can_switch_to_active_linked_account(self):
        LinkedAccount.objects.create(
            owner=self.user1,
            linked_user=self.user2,
            is_active=True,
        )

        self.client.force_authenticate(user=self.user1)

        response = self.client.post(
            '/api/auth/switch-account/',
            {
                'linked_user_id': self.user2.id,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Switched account successfully.')
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['switched_from']['id'], self.user1.id)
        self.assertEqual(response.data['switched_to']['id'], self.user2.id)

    def test_user_cannot_switch_to_unlinked_account(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.post(
            '/api/auth/switch-account/',
            {
                'linked_user_id': self.user3.id,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_cannot_switch_to_inactive_link(self):
        LinkedAccount.objects.create(
            owner=self.user1,
            linked_user=self.user2,
            is_active=False,
        )

        self.client.force_authenticate(user=self.user1)

        response = self.client.post(
            '/api/auth/switch-account/',
            {
                'linked_user_id': self.user2.id,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_switch_token_belongs_to_linked_user(self):
        LinkedAccount.objects.create(
            owner=self.user1,
            linked_user=self.user2,
            is_active=True,
        )

        self.client.force_authenticate(user=self.user1)

        switch_response = self.client.post(
            '/api/auth/switch-account/',
            {
                'linked_user_id': self.user2.id,
            },
            format='json',
        )

        self.assertEqual(switch_response.status_code, status.HTTP_200_OK)

        access_token = switch_response.data['access']

        switched_client = APIClient()
        switched_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )

        profile_response = switched_client.get('/api/auth/profile/')

        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_response.data['user']['id'], self.user2.id)
        self.assertEqual(profile_response.data['user']['username'], self.user2.username)