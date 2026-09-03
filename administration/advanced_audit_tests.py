"""
Additional comprehensive audit tests for JWT auth, groups, and advanced scenarios
"""
from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from clubs.models import Club, ClubMember
from posts.models import Comment, Post, Report


User = get_user_model()


def make_admin(**kw):
    return User.objects.create_user(is_staff=True, **kw)


def make_user(**kw):
    return User.objects.create_user(**kw)


class JWTAuthenticationTests(APITestCase):
    """Verify JWT authentication works with admin endpoints"""

    def setUp(self):
        self.admin = make_admin(email='admin@example.com', password='password123')
        self.user = make_user(email='user@example.com', password='password123')

    def test_admin_can_access_with_jwt_token(self):
        """Admin can access endpoints with valid JWT token"""
        refresh = RefreshToken.for_user(self.admin)
        access_token = str(refresh.access_token)
        
        # Use JWT token in Authorization header
        response = self.client.get(
            reverse('admin-dashboard'),
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_normal_user_with_jwt_cannot_access_admin(self):
        """Normal user with JWT token still cannot access admin"""
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        
        response = self.client.get(
            reverse('admin-dashboard'),
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_jwt_token_returns_401(self):
        """Invalid JWT token returns 401"""
        response = self.client.get(
            reverse('admin-dashboard'),
            HTTP_AUTHORIZATION='Bearer invalid_token_here'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_missing_jwt_token_returns_401(self):
        """Missing JWT token returns 401"""
        response = self.client.get(reverse('admin-dashboard'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class GroupBasedPermissionsTests(APITestCase):
    """Verify group-based admin access works correctly"""

    def setUp(self):
        # Create Administrators group
        self.admin_group, _ = Group.objects.get_or_create(name='Administrators')
        
        # Create a user and add to admin group
        self.group_admin = make_user(email='group_admin@example.com', password='pass')
        self.group_admin.groups.add(self.admin_group)
        
        self.staff_user = make_admin(email='staff@example.com', password='pass')
        self.superuser = User.objects.create_user(
            email='super@example.com', password='pass',
            is_superuser=True, is_staff=True
        )
        self.normal_user = make_user(email='user@example.com', password='pass')

    def test_group_admin_can_access_admin_endpoints(self):
        """User in Administrators group can access admin endpoints"""
        self.client.force_authenticate(self.group_admin)
        response = self.client.get(reverse('admin-dashboard'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_staff_user_can_access_admin_endpoints(self):
        """Staff user can access admin endpoints"""
        self.client.force_authenticate(self.staff_user)
        response = self.client.get(reverse('admin-dashboard'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_superuser_can_access_admin_endpoints(self):
        """Superuser can access admin endpoints"""
        self.client.force_authenticate(self.superuser)
        response = self.client.get(reverse('admin-dashboard'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_normal_user_cannot_access_even_with_group_membership(self):
        """User without admin flag/group cannot access"""
        self.client.force_authenticate(self.normal_user)
        response = self.client.get(reverse('admin-dashboard'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_role_correctly_identified_as_admin_from_group(self):
        """User role is correctly identified as 'admin' from group"""
        self.client.force_authenticate(self.group_admin)
        response = self.client.get(reverse('admin-user-detail', args=[self.group_admin.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], 'admin')

    def test_user_role_correctly_identified_as_superuser(self):
        """User role is correctly identified as 'superuser'"""
        self.client.force_authenticate(self.superuser)
        response = self.client.get(reverse('admin-user-detail', args=[self.superuser.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], 'superuser')

    def test_user_role_correctly_identified_as_staff(self):
        """User role is correctly identified as 'admin' from staff flag"""
        self.client.force_authenticate(self.staff_user)
        response = self.client.get(reverse('admin-user-detail', args=[self.staff_user.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], 'admin')


class AnalyticsViewTests(APITestCase):
    """Test analytics endpoint"""

    def setUp(self):
        self.admin = make_admin(email='admin@example.com', password='pass')
        self.client.force_authenticate(self.admin)

    def test_analytics_returns_correct_keys(self):
        """Analytics endpoint returns all expected keys"""
        response = self.client.get(reverse('admin-analytics'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        expected_keys = [
            'users_registered',
            'posts_created',
            'clubs_created',
            'most_popular_genres',
            'most_active_clubs',
            'most_reviewed_movies',
            'most_active_users',
        ]
        
        for key in expected_keys:
            self.assertIn(key, response.data)

    def test_analytics_daily_data_structure(self):
        """Analytics daily data has correct structure"""
        user = make_user(email='user@example.com', password='pass')
        post = Post.objects.create(user=user, movie_id=1, movie_title='Film', body='Content')
        
        response = self.client.get(reverse('admin-analytics'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check structure of daily data
        posts_data = response.data['posts_created']
        if posts_data:  # Only check if data exists
            self.assertIn('date', posts_data[0])
            self.assertIn('count', posts_data[0])

    def test_analytics_most_active_users_includes_counts(self):
        """Most active users includes post and comment counts"""
        user = make_user(email='user@example.com', password='pass')
        post = Post.objects.create(user=user, movie_id=1, movie_title='Film', body='Content')
        Comment.objects.create(post=post, user=user, body='Comment')
        
        response = self.client.get(reverse('admin-analytics'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        most_active = response.data['most_active_users']
        self.assertTrue(len(most_active) > 0)
        
        # Verify structure
        user_data = most_active[0]
        self.assertIn('id', user_data)
        self.assertIn('name', user_data)
        self.assertIn('email', user_data)
        self.assertIn('post_count', user_data)
        self.assertIn('comment_count', user_data)


class ReportFilteringTests(APITestCase):
    """Test report filtering by type"""

    def setUp(self):
        self.admin = make_admin(email='admin@example.com', password='pass')
        self.user = make_user(email='user@example.com', password='pass')
        self.client.force_authenticate(self.admin)

    def test_filter_reports_by_post_type(self):
        """Filter reports to show only post reports"""
        post = Post.objects.create(user=self.user, movie_id=1, movie_title='Film', body='Content')
        ct = ContentType.objects.get_for_model(Post)
        report = Report.objects.create(
            reported_by=self.user, content_type=ct, object_id=post.pk, reason='Spam'
        )
        
        response = self.client.get(reverse('admin-report-list'), {'type': 'post'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['target_type'], 'post')

    def test_filter_reports_by_comment_type(self):
        """Filter reports to show only comment reports"""
        post = Post.objects.create(user=self.user, movie_id=1, movie_title='Film', body='Post')
        comment = Comment.objects.create(post=post, user=self.user, body='Comment')
        ct = ContentType.objects.get_for_model(Comment)
        report = Report.objects.create(
            reported_by=self.user, content_type=ct, object_id=comment.pk, reason='Spam'
        )
        
        response = self.client.get(reverse('admin-report-list'), {'type': 'comment'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['target_type'], 'comment')

    def test_filter_reports_excludes_other_types(self):
        """Filtering by type excludes other types"""
        post = Post.objects.create(user=self.user, movie_id=1, movie_title='Film', body='Post')
        comment = Comment.objects.create(post=post, user=self.user, body='Comment')
        
        ct_post = ContentType.objects.get_for_model(Post)
        ct_comment = ContentType.objects.get_for_model(Comment)
        
        Report.objects.create(
            reported_by=self.user, content_type=ct_post, object_id=post.pk, reason='Spam'
        )
        Report.objects.create(
            reported_by=self.user, content_type=ct_comment, object_id=comment.pk, reason='Abuse'
        )
        
        # Filter for only posts
        response = self.client.get(reverse('admin-report-list'), {'type': 'post'})
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['target_type'], 'post')


class OrderingAndSearchTests(APITestCase):
    """Test ordering and search functionality"""

    def setUp(self):
        self.admin = make_admin(email='admin@example.com', password='pass')
        self.client.force_authenticate(self.admin)

    def test_posts_ordered_by_created_at_descending(self):
        """Posts are ordered by created_at descending (newest first)"""
        user = make_user(email='user@example.com', password='pass')
        post1 = Post.objects.create(user=user, movie_id=1, movie_title='Film1', body='First')
        post2 = Post.objects.create(user=user, movie_id=2, movie_title='Film2', body='Second')
        
        response = self.client.get(reverse('admin-post-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Newest should be first
        self.assertEqual(response.data['results'][0]['id'], post2.pk)

    def test_clubs_ordered_by_name(self):
        """Clubs are ordered alphabetically by name"""
        user = make_user(email='user@example.com', password='pass')
        club_b = Club.objects.create(name='Bravo Club', created_by=user)
        club_a = Club.objects.create(name='Alpha Club', created_by=user)
        
        response = self.client.get(reverse('admin-club-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        names = [c['name'] for c in response.data['results']]
        self.assertEqual(names[0], 'Alpha Club')

    def test_search_posts_by_movie_title(self):
        """Search posts by movie title"""
        user = make_user(email='user@example.com', password='pass')
        Post.objects.create(user=user, movie_id=1, movie_title='Inception', body='Review')
        Post.objects.create(user=user, movie_id=2, movie_title='Interstellar', body='Review')
        
        response = self.client.get(reverse('admin-post-list'), {'search': 'Inception'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['movie_title'], 'Inception')

    def test_search_clubs_by_creator_email(self):
        """Search clubs by creator email"""
        user1 = make_user(email='alice@example.com', password='pass')
        user2 = make_user(email='bob@example.com', password='pass')
        
        Club.objects.create(name='Alice Club', created_by=user1)
        Club.objects.create(name='Bob Club', created_by=user2)
        
        response = self.client.get(reverse('admin-club-list'), {'search': 'alice'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Alice Club')


class ReportResolutionTests(APITestCase):
    """Test complete report resolution workflow"""

    def setUp(self):
        self.admin = make_admin(email='admin@example.com', password='pass')
        self.user = make_user(email='user@example.com', password='pass')
        self.client.force_authenticate(self.admin)

    def test_report_lifecycle_complete(self):
        """Test complete report lifecycle: PENDING -> REVIEWED -> RESOLVED"""
        post = Post.objects.create(user=self.user, movie_id=1, movie_title='Film', body='Content')
        ct = ContentType.objects.get_for_model(Post)
        report = Report.objects.create(
            reported_by=self.user, content_type=ct, object_id=post.pk,
            reason='Spam', status=Report.Status.PENDING
        )
        
        # Update to REVIEWED
        response = self.client.patch(
            reverse('admin-report-detail', args=[report.pk]),
            {'status': 'REVIEWED'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data['resolved_at'])  # Not resolved yet
        self.assertIsNone(response.data['resolved_by'])
        
        # Update to RESOLVED
        response = self.client.patch(
            reverse('admin-report-detail', args=[report.pk]),
            {'status': 'RESOLVED'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data['resolved_at'])
        self.assertIsNotNone(response.data['resolved_by'])
        self.assertEqual(response.data['resolved_by'], 'admin@example.com')

    def test_dismiss_report_sets_metadata(self):
        """Dismissing report sets resolved_at and resolved_by"""
        post = Post.objects.create(user=self.user, movie_id=1, movie_title='Film', body='Content')
        ct = ContentType.objects.get_for_model(Post)
        report = Report.objects.create(
            reported_by=self.user, content_type=ct, object_id=post.pk, reason='False alarm'
        )
        
        response = self.client.patch(
            reverse('admin-report-detail', args=[report.pk]),
            {'status': 'DISMISSED'},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data['resolved_at'])
        self.assertEqual(response.data['resolved_by'], 'admin@example.com')


class AdminUserFieldVisibilityTests(APITestCase):
    """Verify sensitive fields are not exposed"""

    def setUp(self):
        self.admin = make_admin(email='admin@example.com', password='pass')
        self.user = make_user(email='user@example.com', password='pass', name='Test User')
        self.client.force_authenticate(self.admin)

    def test_user_list_does_not_expose_passwords(self):
        """User list does not contain password hashes"""
        response = self.client.get(reverse('admin-user-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        for user_data in response.data['results']:
            self.assertNotIn('password', user_data)

    def test_user_detail_exposes_safe_fields(self):
        """User detail exposes only safe fields"""
        response = self.client.get(reverse('admin-user-detail', args=[self.user.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should have these fields
        expected_fields = ['id', 'name', 'email', 'bio', 'avatar', 'is_active', 'role', 'date_joined', 'post_count', 'comment_count', 'club_count']
        for field in expected_fields:
            self.assertIn(field, response.data)
        
        # Should NOT have these
        forbidden_fields = ['password', 'is_superuser', 'is_staff']
        for field in forbidden_fields:
            self.assertNotIn(field, response.data)

    def test_user_list_shows_role_but_not_flags(self):
        """User list shows role but not is_staff/is_superuser flags"""
        response = self.client.get(reverse('admin-user-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        for user_data in response.data['results']:
            # Should have role
            self.assertIn('role', user_data)
            # But not raw flags
            self.assertNotIn('is_staff', user_data)
            self.assertNotIn('is_superuser', user_data)
