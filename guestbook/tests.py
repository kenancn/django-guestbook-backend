from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import GuestbookUser, GuestbookEntry

class GuestbookTests(APITestCase):
    def setUp(self):
        # Create a test user and entry
        self.user = GuestbookUser.objects.create(name="Test User")
        self.entry = GuestbookEntry.objects.create(
            user=self.user,
            subject="Test Subject",
            message="Test Message"
        )

    def test_create_entry(self):
        """
        Test creating a new guestbook entry.
        """
        url = reverse('entries')
        data = {
            'name': 'John Doe',
            'subject': 'Hello',
            'message': 'Hello World!'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(GuestbookEntry.objects.count(), 2)
        self.assertEqual(GuestbookUser.objects.get(name='John Doe').name, 'John Doe')

    def test_get_entries(self):
        """
        Test getting the list of entries.
        """
        url = reverse('entries')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['entries'][0]['subject'], 'Test Subject')

    def test_get_users_data(self):
        """
        Test getting users data.
        """
        url = reverse('users-data')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['users']), 1)
        self.assertEqual(response.data['users'][0]['username'], 'Test User')

    def test_invalid_entry_creation(self):
        """
        Test validation rules for entry creation.
        """
        url = reverse('entries')
        
        # Test invalid name
        data = {
            'name': 'John123',  # numbers not allowed
            'subject': 'Hello',
            'message': 'Hello World!'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test short message
        data = {
            'name': 'John',
            'subject': 'Hello',
            'message': 'Hi'  # too short
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test duplicate message spam
        data = {
            'name': 'John',
            'subject': 'Hello',
            'message': 'This is a test message'
        }
        self.client.post(url, data, format='json')
        response = self.client.post(url, data, format='json')  # same message within 5 minutes
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) 