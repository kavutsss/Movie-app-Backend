from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import User


class AccountsApiTests(APITestCase):
	def test_register_and_login(self):
		response = self.client.post(reverse('register'), {
			'name': 'Ava', 'email': 'ava@example.com', 'password': 'strong-pass-123',
		})
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		response = self.client.post(reverse('login'), {
			'email': 'ava@example.com', 'password': 'strong-pass-123',
		})
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertIn('access', response.data)

	def test_follow_and_unfollow(self):
		first = User.objects.create_user(email='first@example.com', password='strong-pass-123')
		second = User.objects.create_user(email='second@example.com', password='strong-pass-123')
		self.client.force_authenticate(first)
		response = self.client.post(reverse('user-follow', args=[second.pk]))
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertTrue(first.following.filter(pk=second.pk).exists())
		self.assertEqual(self.client.delete(reverse('user-follow', args=[second.pk])).status_code, status.HTTP_204_NO_CONTENT)
