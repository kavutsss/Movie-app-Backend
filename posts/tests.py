from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from .models import Post


class PostsApiTests(APITestCase):
	def setUp(self):
		self.user = User.objects.create_user(email='critic@example.com', password='strong-pass-123')
		self.client.force_authenticate(self.user)

	def test_create_like_comment_and_delete_post(self):
		post = self.client.post(reverse('post-list'), {
			'movie_id': 11, 'movie_title': 'A Film', 'body': 'Worth watching', 'stars': 5,
		})
		self.assertEqual(post.status_code, status.HTTP_201_CREATED)
		post_id = post.data['id']
		self.assertEqual(self.client.post(reverse('post-like', args=[post_id])).data['like_count'], 1)
		comment = self.client.post(reverse('comment-list', args=[post_id]), {'body': 'Agreed'})
		self.assertEqual(comment.status_code, status.HTTP_201_CREATED)
		self.assertEqual(self.client.delete(reverse('post-detail', args=[post_id])).status_code, status.HTTP_204_NO_CONTENT)

	def test_stars_are_limited_to_five(self):
		response = self.client.post(reverse('post-list'), {
			'movie_id': 11, 'movie_title': 'A Film', 'body': 'Too much', 'stars': 6,
		})
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)