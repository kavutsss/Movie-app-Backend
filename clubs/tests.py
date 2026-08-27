from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from .models import ClubMember


class ClubsApiTests(APITestCase):
	def setUp(self):
		self.user = User.objects.create_user(email='leader@example.com', password='strong-pass-123')
		self.client.force_authenticate(self.user)

	def test_create_join_and_leave_club(self):
		response = self.client.post(reverse('club-list'), {'name': 'Sci-Fi', 'genre': 'Science fiction'})
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		club_id = response.data['id']
		self.assertEqual(ClubMember.objects.filter(club_id=club_id).count(), 1)
		self.assertEqual(self.client.post(reverse('club-membership', args=[club_id])).status_code, status.HTTP_201_CREATED)
		self.assertEqual(self.client.delete(reverse('club-membership', args=[club_id])).status_code, status.HTTP_204_NO_CONTENT)

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User


class WatchlistApiTests(APITestCase):
	def setUp(self):
		self.user = User.objects.create_user(email='viewer@example.com', password='strong-pass-123')
		self.client.force_authenticate(self.user)

	def test_add_and_remove_movie(self):
		response = self.client.post(reverse('watchlist-list'), {
			'movie_id': 42, 'movie_title': 'The Answer', 'poster_path': '/poster.jpg',
		})
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(self.client.delete(reverse('watchlist-detail', args=[response.data['id']])).status_code, status.HTTP_204_NO_CONTENT)

	def test_anonymous_user_is_rejected(self):
		self.client.force_authenticate(None)
		response = self.client.get(reverse('watchlist-list'))
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
