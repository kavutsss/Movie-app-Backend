from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from clubs.models import Club
from posts.models import Comment, Post, Report
from django.contrib.contenttypes.models import ContentType


def make_admin(**kw):
    return User.objects.create_user(is_staff=True, **kw)


def make_user(**kw):
    return User.objects.create_user(**kw)


class AdminAuthTests(APITestCase):
    """401 for anonymous, 403 for normal users, 200 for admins."""

    def setUp(self):
        self.admin = make_admin(email='admin@example.com', password='pass')
        self.user = make_user(email='user@example.com', password='pass')

    def _assert_access(self, url_name, *args):
        url = reverse(url_name, args=args) if args else reverse(url_name)
        self.assertEqual(self.client.get(url).status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.get(url).status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(self.admin)
        self.assertIn(self.client.get(url).status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])
        self.client.force_authenticate(None)

    def test_dashboard_access(self):
        self._assert_access('admin-dashboard')

    def test_user_list_access(self):
        self._assert_access('admin-user-list')

    def test_club_list_access(self):
        self._assert_access('admin-club-list')

    def test_post_list_access(self):
        self._assert_access('admin-post-list')

    def test_report_list_access(self):
        self._assert_access('admin-report-list')

    def test_analytics_access(self):
        self._assert_access('admin-analytics')


class AdminDashboardTests(APITestCase):
    def setUp(self):
        self.admin = make_admin(email='admin@example.com', password='pass')
        self.u1 = make_user(email='u1@example.com', password='pass')
        self.u2 = make_user(email='u2@example.com', password='pass', is_active=False)
        self.club = Club.objects.create(name='C1', created_by=self.u1)
        self.post = Post.objects.create(user=self.u1, movie_id=1, movie_title='Film', body='Good', stars=4)
        self.client.force_authenticate(self.admin)

    def test_dashboard_statistics(self):
        r = self.client.get(reverse('admin-dashboard'))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        stats = r.data['statistics']
        self.assertEqual(stats['total_users'], 3)   # admin + u1 + u2
        self.assertEqual(stats['active_users'], 2)
        self.assertEqual(stats['inactive_users'], 1)
        self.assertEqual(stats['total_clubs'], 1)
        self.assertEqual(stats['total_posts'], 1)

    def test_dashboard_recent_activity_keys(self):
        r = self.client.get(reverse('admin-dashboard'))
        self.assertIn('recent_activity', r.data)
        for key in ('users', 'posts', 'clubs', 'reports'):
            self.assertIn(key, r.data['recent_activity'])


class AdminUserManagementTests(APITestCase):
    def setUp(self):
        self.admin = make_admin(email='admin@example.com', password='pass')
        self.user = make_user(email='regular@example.com', password='pass')
        self.client.force_authenticate(self.admin)

    def test_list_users(self):
        r = self.client.get(reverse('admin-user-list'))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn('results', r.data)

    def test_search_users(self):
        r = self.client.get(reverse('admin-user-list'), {'search': 'regular'})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        emails = [u['email'] for u in r.data['results']]
        self.assertIn('regular@example.com', emails)

    def test_filter_by_status_active(self):
        r = self.client.get(reverse('admin-user-list'), {'status': 'active'})
        self.assertTrue(all(u['is_active'] for u in r.data['results']))

    def test_deactivate_user(self):
        r = self.client.patch(reverse('admin-user-status', args=[self.user.pk]), {'is_active': False}, format='json')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertFalse(r.data['is_active'])

    def test_activate_user(self):
        self.user.is_active = False
        self.user.save()
        r = self.client.patch(reverse('admin-user-status', args=[self.user.pk]), {'is_active': True}, format='json')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertTrue(r.data['is_active'])

    def test_cannot_deactivate_last_superuser(self):
        su = User.objects.create_user(email='su@example.com', password='pass', is_superuser=True, is_staff=True)
        r = self.client.patch(reverse('admin-user-status', args=[su.pk]), {'is_active': False}, format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_delete_last_superuser(self):
        su = User.objects.create_user(email='su@example.com', password='pass', is_superuser=True, is_staff=True)
        r = self.client.delete(reverse('admin-user-detail', args=[su.pk]))
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_regular_user(self):
        r = self.client.delete(reverse('admin-user-detail', args=[self.user.pk]))
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_detail_includes_counts(self):
        r = self.client.get(reverse('admin-user-detail', args=[self.user.pk]))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        for field in ('post_count', 'comment_count', 'club_count'):
            self.assertIn(field, r.data)

    def test_status_field_must_be_boolean(self):
        r = self.client.patch(reverse('admin-user-status', args=[self.user.pk]), {'is_active': 'yes'}, format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)


class AdminClubManagementTests(APITestCase):
    def setUp(self):
        self.admin = make_admin(email='admin@example.com', password='pass')
        self.owner = make_user(email='owner@example.com', password='pass')
        self.club = Club.objects.create(name='Test Club', genre='Drama', created_by=self.owner)
        self.client.force_authenticate(self.admin)

    def test_list_clubs(self):
        r = self.client.get(reverse('admin-club-list'))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['count'], 1)

    def test_search_clubs(self):
        r = self.client.get(reverse('admin-club-list'), {'search': 'Test'})
        self.assertEqual(r.data['results'][0]['name'], 'Test Club')

    def test_filter_clubs_by_status(self):
        r = self.client.get(reverse('admin-club-list'), {'status': 'ACTIVE'})
        self.assertTrue(all(c['status'] == 'ACTIVE' for c in r.data['results']))

    def test_suspend_club(self):
        r = self.client.patch(reverse('admin-club-status', args=[self.club.pk]), {'status': 'SUSPENDED'}, format='json')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['status'], 'SUSPENDED')

    def test_reactivate_club(self):
        self.club.status = Club.Status.SUSPENDED
        self.club.save()
        r = self.client.patch(reverse('admin-club-status', args=[self.club.pk]), {'status': 'ACTIVE'}, format='json')
        self.assertEqual(r.data['status'], 'ACTIVE')

    def test_invalid_club_status(self):
        r = self.client.patch(reverse('admin-club-status', args=[self.club.pk]), {'status': 'BANNED'}, format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_club(self):
        r = self.client.delete(reverse('admin-club-detail', args=[self.club.pk]))
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)

    def test_club_detail_includes_members(self):
        r = self.client.get(reverse('admin-club-detail', args=[self.club.pk]))
        self.assertIn('members', r.data)


class AdminPostModerationTests(APITestCase):
    def setUp(self):
        self.admin = make_admin(email='admin@example.com', password='pass')
        self.user = make_user(email='poster@example.com', password='pass')
        self.post = Post.objects.create(user=self.user, movie_id=1, movie_title='Film', body='Review')
        self.client.force_authenticate(self.admin)

    def test_list_posts(self):
        r = self.client.get(reverse('admin-post-list'))
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_hide_post(self):
        r = self.client.patch(reverse('admin-post-moderate', args=[self.post.pk]), {'status': 'HIDDEN'}, format='json')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['status'], 'HIDDEN')

    def test_restore_post(self):
        self.post.status = Post.ModerationStatus.HIDDEN
        self.post.save()
        r = self.client.patch(reverse('admin-post-moderate', args=[self.post.pk]), {'status': 'VISIBLE'}, format='json')
        self.assertEqual(r.data['status'], 'VISIBLE')

    def test_invalid_post_status(self):
        r = self.client.patch(reverse('admin-post-moderate', args=[self.post.pk]), {'status': 'DELETED'}, format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_post(self):
        r = self.client.delete(reverse('admin-post-delete', args=[self.post.pk]))
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)

    def test_filter_posts_by_status(self):
        self.post.status = Post.ModerationStatus.HIDDEN
        self.post.save()
        r = self.client.get(reverse('admin-post-list'), {'status': 'HIDDEN'})
        self.assertTrue(all(p['status'] == 'HIDDEN' for p in r.data['results']))


class AdminCommentModerationTests(APITestCase):
    def setUp(self):
        self.admin = make_admin(email='admin@example.com', password='pass')
        self.user = make_user(email='commenter@example.com', password='pass')
        self.post = Post.objects.create(user=self.user, movie_id=1, movie_title='Film', body='Review')
        self.comment = Comment.objects.create(post=self.post, user=self.user, body='Nice!')
        self.client.force_authenticate(self.admin)

    def test_list_comments(self):
        r = self.client.get(reverse('admin-comment-list'))
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_hide_comment(self):
        r = self.client.patch(reverse('admin-comment-moderate', args=[self.comment.pk]), {'status': 'HIDDEN'}, format='json')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['status'], 'HIDDEN')

    def test_delete_comment(self):
        r = self.client.delete(reverse('admin-comment-delete', args=[self.comment.pk]))
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)


class AdminReportTests(APITestCase):
    def setUp(self):
        self.admin = make_admin(email='admin@example.com', password='pass')
        self.user = make_user(email='reporter@example.com', password='pass')
        self.post = Post.objects.create(user=self.user, movie_id=1, movie_title='Film', body='Review')
        ct = ContentType.objects.get_for_model(Post)
        self.report = Report.objects.create(
            reported_by=self.user, content_type=ct, object_id=self.post.pk,
            reason='Spam', description='Repeated spam content',
        )
        self.client.force_authenticate(self.admin)

    def test_list_reports(self):
        r = self.client.get(reverse('admin-report-list'))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['count'], 1)

    def test_filter_reports_by_status(self):
        r = self.client.get(reverse('admin-report-list'), {'status': 'PENDING'})
        self.assertTrue(all(rep['status'] == 'PENDING' for rep in r.data['results']))

    def test_filter_reports_by_type(self):
        r = self.client.get(reverse('admin-report-list'), {'type': 'post'})
        self.assertEqual(r.data['count'], 1)

    def test_resolve_report(self):
        r = self.client.patch(reverse('admin-report-detail', args=[self.report.pk]), {'status': 'RESOLVED'}, format='json')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['status'], 'RESOLVED')

    def test_dismiss_report(self):
        r = self.client.patch(reverse('admin-report-detail', args=[self.report.pk]), {'status': 'DISMISSED'}, format='json')
        self.assertEqual(r.data['status'], 'DISMISSED')

    def test_report_detail(self):
        r = self.client.get(reverse('admin-report-detail', args=[self.report.pk]))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['reason'], 'Spam')
        self.assertEqual(r.data['target_type'], 'post')


class AdminAnalyticsTests(APITestCase):
    def setUp(self):
        self.admin = make_admin(email='admin@example.com', password='pass')
        self.client.force_authenticate(self.admin)

    def test_analytics_keys(self):
        r = self.client.get(reverse('admin-analytics'))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        for key in ('users_registered', 'posts_created', 'clubs_created',
                    'most_popular_genres', 'most_active_clubs',
                    'most_reviewed_movies', 'most_active_users'):
            self.assertIn(key, r.data)


class AdminReviewListTests(APITestCase):
    def setUp(self):
        self.admin = make_admin(email='admin@example.com', password='pass')
        self.user = make_user(email='reviewer@example.com', password='pass')
        Post.objects.create(user=self.user, movie_id=1, movie_title='Film', body='Great', stars=5)
        Post.objects.create(user=self.user, movie_id=2, movie_title='Film2', body='No stars')
        self.client.force_authenticate(self.admin)

    def test_reviews_only_include_starred_posts(self):
        r = self.client.get(reverse('admin-review-list'))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertTrue(all(p['stars'] is not None for p in r.data['results']))
        self.assertEqual(r.data['count'], 1)
