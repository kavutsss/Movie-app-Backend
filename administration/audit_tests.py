"""
Comprehensive Admin Backend Audit Tests
Tests database persistence, security, efficiency, and edge cases
"""
from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from clubs.models import Club, ClubMember
from posts.models import Comment, Post, Report
from administration.serializers import AdminUserSerializer


User = get_user_model()


def make_admin(**kw):
    return User.objects.create_user(is_staff=True, **kw)


def make_user(**kw):
    return User.objects.create_user(**kw)


class DatabasePersistenceTests(APITestCase):
    """Verify that all admin CRUD operations persist to database correctly"""

    def setUp(self):
        self.admin = make_admin(email='admin@example.com', password='pass123')
        self.client.force_authenticate(self.admin)

    def test_user_update_persists_to_database(self):
        """Verify that user updates persist correctly"""
        user = make_user(email='user@example.com', password='pass')
        new_name = 'Updated Name'
        new_bio = 'Updated Bio'
        
        # Update through API
        response = self.client.patch(
            reverse('admin-user-detail', args=[user.pk]),
            {'name': new_name, 'bio': new_bio},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Query database directly to verify
        user_from_db = User.objects.get(pk=user.pk)
        self.assertEqual(user_from_db.name, new_name)
        self.assertEqual(user_from_db.bio, new_bio)

    def test_club_status_change_persists_to_database(self):
        """Verify club status changes persist"""
        user = make_user(email='owner@example.com', password='pass')
        club = Club.objects.create(name='Test Club', created_by=user, status=Club.Status.ACTIVE)
        
        # Change status through API
        response = self.client.patch(
            reverse('admin-club-status', args=[club.pk]),
            {'status': 'SUSPENDED'},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify in database
        club_from_db = Club.objects.get(pk=club.pk)
        self.assertEqual(club_from_db.status, Club.Status.SUSPENDED)

    def test_post_moderation_status_persists_to_database(self):
        """Verify post moderation status changes persist"""
        user = make_user(email='poster@example.com', password='pass')
        post = Post.objects.create(
            user=user, movie_id=1, movie_title='Film', 
            body='Content', status=Post.ModerationStatus.VISIBLE
        )
        
        # Moderate post through API
        response = self.client.patch(
            reverse('admin-post-moderate', args=[post.pk]),
            {'status': 'HIDDEN'},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify in database
        post_from_db = Post.objects.get(pk=post.pk)
        self.assertEqual(post_from_db.status, Post.ModerationStatus.HIDDEN)

    def test_report_resolution_persists_with_metadata(self):
        """Verify report resolution persists with admin metadata"""
        reporter = make_user(email='reporter@example.com', password='pass')
        post = Post.objects.create(user=reporter, movie_id=1, movie_title='Film', body='Content')
        ct = ContentType.objects.get_for_model(Post)
        report = Report.objects.create(
            reported_by=reporter, content_type=ct, object_id=post.pk,
            reason='Spam', status=Report.Status.PENDING
        )
        
        # Resolve report through API
        response = self.client.patch(
            reverse('admin-report-detail', args=[report.pk]),
            {'status': 'RESOLVED'},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify in database with correct admin metadata
        report_from_db = Report.objects.get(pk=report.pk)
        self.assertEqual(report_from_db.status, Report.Status.RESOLVED)
        self.assertIsNotNone(report_from_db.resolved_at)
        self.assertEqual(report_from_db.resolved_by, self.admin)

    def test_comment_moderation_persists_to_database(self):
        """Verify comment moderation status persists"""
        user = make_user(email='commenter@example.com', password='pass')
        post = Post.objects.create(user=user, movie_id=1, movie_title='Film', body='Post')
        comment = Comment.objects.create(
            post=post, user=user, body='Comment', 
            status=Comment.ModerationStatus.VISIBLE
        )
        
        # Moderate through API
        response = self.client.patch(
            reverse('admin-comment-moderate', args=[comment.pk]),
            {'status': 'REMOVED'},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify in database
        comment_from_db = Comment.objects.get(pk=comment.pk)
        self.assertEqual(comment_from_db.status, Comment.ModerationStatus.REMOVED)


class SecurityTests(APITestCase):
    """Verify security constraints and authorization"""

    def setUp(self):
        self.admin = make_admin(email='admin@example.com', password='pass123')
        self.user = make_user(email='user@example.com', password='pass123')

    def test_normal_user_cannot_access_admin_dashboard(self):
        """Verify normal user cannot access admin dashboard"""
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('admin-dashboard'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_normal_user_cannot_moderate_posts(self):
        """Verify normal user cannot moderate posts"""
        post = Post.objects.create(user=self.user, movie_id=1, movie_title='Film', body='Content')
        self.client.force_authenticate(self.user)
        
        response = self.client.patch(
            reverse('admin-post-moderate', args=[post.pk]),
            {'status': 'HIDDEN'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_normal_user_cannot_delete_users(self):
        """Verify normal user cannot delete users"""
        other_user = make_user(email='other@example.com', password='pass')
        self.client.force_authenticate(self.user)
        
        response = self.client.delete(reverse('admin-user-detail', args=[other_user.pk]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_access_admin_endpoints(self):
        """Verify unauthenticated users get 401"""
        response = self.client.get(reverse('admin-dashboard'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_cannot_access_own_account_detail_via_admin(self):
        """Admin should not expose user passwords or sensitive fields"""
        self.client.force_authenticate(self.admin)
        response = self.client.get(reverse('admin-user-detail', args=[self.user.pk]))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify no password hash is exposed
        self.assertNotIn('password', response.data)

    def test_admin_cannot_modify_email_field(self):
        """Email should be immutable through admin API"""
        self.client.force_authenticate(self.admin)
        original_email = self.user.email
        
        response = self.client.patch(
            reverse('admin-user-detail', args=[self.user.pk]),
            {'email': 'newemail@example.com'},
            format='json'
        )
        
        # Verify email was not changed
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, original_email)

    def test_admin_cannot_modify_superuser_flag(self):
        """is_superuser should not be modifiable through admin API"""
        regular_admin = make_admin(email='regular_admin@example.com', password='pass')
        self.client.force_authenticate(regular_admin)
        
        response = self.client.patch(
            reverse('admin-user-detail', args=[self.user.pk]),
            {'is_superuser': True},
            format='json'
        )
        
        # Verify superuser flag was not changed
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_superuser)

    def test_admin_cannot_modify_staff_flag(self):
        """is_staff should not be modifiable through admin API"""
        regular_admin = make_admin(email='regular_admin@example.com', password='pass')
        self.client.force_authenticate(regular_admin)
        
        response = self.client.patch(
            reverse('admin-user-detail', args=[self.user.pk]),
            {'is_staff': True},
            format='json'
        )
        
        # Verify staff flag was not changed
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_staff)


class DashboardAccuracyTests(APITestCase):
    """Verify dashboard statistics are accurate"""

    def setUp(self):
        self.admin = make_admin(email='admin@example.com', password='pass')
        self.client.force_authenticate(self.admin)

    def test_dashboard_user_counts_are_accurate(self):
        """Verify total/active/inactive user counts"""
        # Create users with different states
        active_user1 = make_user(email='active1@example.com', password='pass', is_active=True)
        active_user2 = make_user(email='active2@example.com', password='pass', is_active=True)
        inactive_user = make_user(email='inactive@example.com', password='pass', is_active=False)
        
        response = self.client.get(reverse('admin-dashboard'))
        stats = response.data['statistics']
        
        # Count includes admin + 3 created users
        self.assertEqual(stats['total_users'], 4)
        self.assertEqual(stats['active_users'], 3)
        self.assertEqual(stats['inactive_users'], 1)

    def test_dashboard_movie_count_accuracy(self):
        """Verify unique movie count is accurate"""
        user = make_user(email='user@example.com', password='pass')
        
        # Create posts for 2 different movies
        Post.objects.create(user=user, movie_id=1, movie_title='Film1', body='Review1')
        Post.objects.create(user=user, movie_id=1, movie_title='Film1', body='Review2')  # Same movie
        Post.objects.create(user=user, movie_id=2, movie_title='Film2', body='Review3')  # Different movie
        
        response = self.client.get(reverse('admin-dashboard'))
        stats = response.data['statistics']
        
        # Should count unique movies only
        self.assertEqual(stats['total_movies'], 2)

    def test_dashboard_club_count_accuracy(self):
        """Verify club count is accurate"""
        user = make_user(email='user@example.com', password='pass')
        Club.objects.create(name='Club1', created_by=user)
        Club.objects.create(name='Club2', created_by=user)
        
        response = self.client.get(reverse('admin-dashboard'))
        stats = response.data['statistics']
        
        self.assertEqual(stats['total_clubs'], 2)

    def test_dashboard_post_count_accuracy(self):
        """Verify total post count"""
        user = make_user(email='user@example.com', password='pass')
        Post.objects.create(user=user, movie_id=1, movie_title='Film1', body='Post1')
        Post.objects.create(user=user, movie_id=1, movie_title='Film1', body='Post2')
        
        response = self.client.get(reverse('admin-dashboard'))
        stats = response.data['statistics']
        
        self.assertEqual(stats['total_posts'], 2)

    def test_dashboard_comment_count_accuracy(self):
        """Verify comment count accuracy"""
        user = make_user(email='user@example.com', password='pass')
        post = Post.objects.create(user=user, movie_id=1, movie_title='Film', body='Post')
        Comment.objects.create(post=post, user=user, body='Comment1')
        Comment.objects.create(post=post, user=user, body='Comment2')
        
        response = self.client.get(reverse('admin-dashboard'))
        stats = response.data['statistics']
        
        # Reviews + comments = posts with stars + all comments
        self.assertEqual(stats['total_reviews_comments'], 2)

    def test_dashboard_pending_report_count_accuracy(self):
        """Verify pending report count"""
        user = make_user(email='user@example.com', password='pass')
        post = Post.objects.create(user=user, movie_id=1, movie_title='Film', body='Content')
        ct = ContentType.objects.get_for_model(Post)
        
        # Create different statuses
        Report.objects.create(reported_by=user, content_type=ct, object_id=post.pk, reason='Spam', status=Report.Status.PENDING)
        Report.objects.create(reported_by=user, content_type=ct, object_id=post.pk, reason='Spam', status=Report.Status.REVIEWED)
        Report.objects.create(reported_by=user, content_type=ct, object_id=post.pk, reason='Spam', status=Report.Status.PENDING)
        
        response = self.client.get(reverse('admin-dashboard'))
        stats = response.data['statistics']
        
        self.assertEqual(stats['pending_reports'], 2)


class QueryEfficiencyTests(APITestCase):
    """Verify queries are efficient (no N+1 problems)"""

    def setUp(self):
        self.admin = make_admin(email='admin@example.com', password='pass')
        self.client.force_authenticate(self.admin)

    def test_user_list_uses_reasonable_queries(self):
        """Verify user list doesn't have N+1 query problems"""
        # Create multiple users
        for i in range(10):
            make_user(email=f'user{i}@example.com', password='pass')
        
        with CaptureQueriesContext(connection) as context:
            response = self.client.get(reverse('admin-user-list'))
        
        # Should have limited queries despite many users
        # Estimate: ~1-2 queries for main fetch + group checking
        # Should not be one query per user
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # This is a sanity check - with prefetch_related, should be < 10 queries for 10 users
        self.assertLess(len(context.captured_queries), 20)

    def test_club_list_uses_reasonable_queries(self):
        """Verify club list doesn't have N+1 query problems"""
        user = make_user(email='user@example.com', password='pass')
        
        # Create clubs with members
        for i in range(5):
            club = Club.objects.create(name=f'Club{i}', created_by=user)
            # Add some members
            for j in range(3):
                member = make_user(email=f'member{i}_{j}@example.com', password='pass')
                ClubMember.objects.create(club=club, user=member)
        
        with CaptureQueriesContext(connection) as context:
            response = self.client.get(reverse('admin-club-list'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should be efficient despite members
        self.assertLess(len(context.captured_queries), 20)

    def test_post_list_uses_reasonable_queries(self):
        """Verify post list doesn't have N+1 query problems"""
        user = make_user(email='user@example.com', password='pass')
        
        # Create multiple posts
        for i in range(10):
            post = Post.objects.create(user=user, movie_id=i, movie_title=f'Film{i}', body=f'Content{i}')
            # Add comments and likes
            for j in range(2):
                Comment.objects.create(post=post, user=user, body=f'Comment{j}')
            post.likes.add(user)
        
        with CaptureQueriesContext(connection) as context:
            response = self.client.get(reverse('admin-post-list'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should handle 10 posts with comments and likes efficiently
        self.assertLess(len(context.captured_queries), 20)


class DataValidationTests(APITestCase):
    """Verify data validation and error handling"""

    def setUp(self):
        self.admin = make_admin(email='admin@example.com', password='pass')
        self.client.force_authenticate(self.admin)

    def test_invalid_user_id_returns_404(self):
        """Verify invalid user ID returns 404"""
        response = self.client.get(reverse('admin-user-detail', args=[99999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_club_id_returns_404(self):
        """Verify invalid club ID returns 404"""
        response = self.client.get(reverse('admin-club-detail', args=[99999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_post_status_value_returns_400(self):
        """Verify invalid status value returns proper error"""
        user = make_user(email='user@example.com', password='pass')
        post = Post.objects.create(user=user, movie_id=1, movie_title='Film', body='Content')
        
        response = self.client.patch(
            reverse('admin-post-moderate', args=[post.pk]),
            {'status': 'INVALID_STATUS'},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('status', response.data)

    def test_invalid_club_status_value_returns_400(self):
        """Verify invalid club status value returns proper error"""
        user = make_user(email='user@example.com', password='pass')
        club = Club.objects.create(name='Club', created_by=user)
        
        response = self.client.patch(
            reverse('admin-club-status', args=[club.pk]),
            {'status': 'INVALID'},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('status', response.data)

    def test_invalid_is_active_type_returns_400(self):
        """Verify non-boolean is_active returns 400"""
        user = make_user(email='user@example.com', password='pass')
        
        response = self.client.patch(
            reverse('admin-user-status', args=[user.pk]),
            {'is_active': 'true'},  # String instead of boolean
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_required_fields_in_report_update(self):
        """Verify updating with missing required fields"""
        user = make_user(email='user@example.com', password='pass')
        post = Post.objects.create(user=user, movie_id=1, movie_title='Film', body='Content')
        ct = ContentType.objects.get_for_model(Post)
        report = Report.objects.create(
            reported_by=user, content_type=ct, object_id=post.pk, reason='Spam'
        )
        
        # Empty status should still work (no change)
        response = self.client.patch(
            reverse('admin-report-detail', args=[report.pk]),
            {},
            format='json'
        )
        
        # Should be successful (no error on empty update)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class EdgeCaseTests(APITestCase):
    """Verify edge cases and corner scenarios"""

    def setUp(self):
        self.admin = make_admin(email='admin@example.com', password='pass')
        self.client.force_authenticate(self.admin)

    def test_cannot_delete_own_admin_account(self):
        """Admin cannot delete their own account"""
        response = self.client.delete(reverse('admin-user-detail', args=[self.admin.pk]))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Verify account still exists
        self.assertTrue(User.objects.filter(pk=self.admin.pk).exists())

    def test_cannot_deactivate_own_admin_account(self):
        """Admin cannot deactivate their own account"""
        response = self.client.patch(
            reverse('admin-user-status', args=[self.admin.pk]),
            {'is_active': False},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Verify account is still active
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_active)

    def test_delete_club_with_members(self):
        """Verify deleting club with members works correctly"""
        user = make_user(email='user@example.com', password='pass')
        club = Club.objects.create(name='Club', created_by=user)
        
        # Add members
        for i in range(5):
            member = make_user(email=f'member{i}@example.com', password='pass')
            ClubMember.objects.create(club=club, user=member)
        
        # Delete club
        response = self.client.delete(reverse('admin-club-detail', args=[club.pk]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify club and members are deleted
        self.assertFalse(Club.objects.filter(pk=club.pk).exists())
        self.assertFalse(ClubMember.objects.filter(club__pk=club.pk).exists())

    def test_delete_post_with_comments_and_likes(self):
        """Verify deleting post with comments and likes"""
        user = make_user(email='user@example.com', password='pass')
        post = Post.objects.create(user=user, movie_id=1, movie_title='Film', body='Content')
        
        # Add comments and likes
        comment = Comment.objects.create(post=post, user=user, body='Comment')
        post.likes.add(user)
        
        # Delete post
        response = self.client.delete(reverse('admin-post-delete', args=[post.pk]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify post and comments are deleted
        self.assertFalse(Post.objects.filter(pk=post.pk).exists())
        self.assertFalse(Comment.objects.filter(pk=comment.pk).exists())

    def test_filter_users_by_active_status(self):
        """Verify filtering by active status works correctly"""
        active_user = make_user(email='active@example.com', password='pass', is_active=True)
        inactive_user = make_user(email='inactive@example.com', password='pass', is_active=False)
        
        # Filter for active
        response = self.client.get(reverse('admin-user-list'), {'status': 'active'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        emails = [u['email'] for u in response.data['results']]
        self.assertIn('active@example.com', emails)
        self.assertNotIn('inactive@example.com', emails)
        
        # Filter for inactive
        response = self.client.get(reverse('admin-user-list'), {'status': 'inactive'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        emails = [u['email'] for u in response.data['results']]
        self.assertNotIn('active@example.com', emails)
        self.assertIn('inactive@example.com', emails)

    def test_pagination_works_correctly(self):
        """Verify pagination limits results"""
        # Create 25 users (more than default page size of 20)
        for i in range(24):
            make_user(email=f'user{i}@example.com', password='pass')
        
        response = self.client.get(reverse('admin-user-list'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # First page should have 20 results
        self.assertEqual(len(response.data['results']), 20)
        # Should indicate more pages available
        self.assertIsNotNone(response.data['next'])

    def test_search_finds_users_by_email(self):
        """Verify search finds users by email"""
        user = make_user(email='searchtest@example.com', password='pass')
        
        response = self.client.get(
            reverse('admin-user-list'),
            {'search': 'searchtest'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        emails = [u['email'] for u in response.data['results']]
        self.assertIn('searchtest@example.com', emails)

    def test_search_finds_users_by_name(self):
        """Verify search finds users by name"""
        user = make_user(email='user@example.com', password='pass', name='John Doe')
        
        response = self.client.get(
            reverse('admin-user-list'),
            {'search': 'John'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [u['name'] for u in response.data['results']]
        self.assertIn('John Doe', names)
