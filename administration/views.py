from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework import filters, generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from clubs.models import Club
from posts.models import Comment, Post, Report
from .models import ActivityLog
from .permissions import IsPlatformAdmin
from .serializers import (ActivityLogSerializer, AdminClubSerializer, AdminCommentSerializer, AdminMovieSerializer,
                          AdminPostSerializer,
                          AdminReportSerializer, AdminUserSerializer)

User = get_user_model()


class AdminPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class AdminListAPIView(generics.ListAPIView):
    permission_classes = [IsPlatformAdmin]
    pagination_class = AdminPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]


def user_queryset():
    return User.objects.prefetch_related('groups').annotate(
        post_count=Count('posts', distinct=True),
        comment_count=Count('comments', distinct=True),
        club_count=Count('club_memberships', distinct=True),
    ).order_by('-date_joined')


class DashboardView(APIView):
    permission_classes = [IsPlatformAdmin]

    def get(self, request):
        return Response({
            'statistics': {
                'total_users': User.objects.count(),
                'active_users': User.objects.filter(is_active=True).count(),
                'inactive_users': User.objects.filter(is_active=False).count(),
                'total_movies': Post.objects.values('movie_id').distinct().count(),
                'total_tv_series': 0,
                'total_clubs': Club.objects.count(),
                'total_posts': Post.objects.count(),
                'total_reviews_comments': Post.objects.filter(stars__isnull=False).count() + Comment.objects.count(),
                'pending_reports': Report.objects.filter(status=Report.Status.PENDING).count(),
            },
            'recent_activity': {
                'activities': ActivityLogSerializer(ActivityLog.objects.select_related('actor', 'review')[:10], many=True).data,
                'users': AdminUserSerializer(user_queryset()[:5], many=True).data,
                'posts': AdminPostSerializer(Post.objects.select_related('user').annotate(
                    like_count=Count('likes', distinct=True), comment_count=Count('comments', distinct=True))[:5], many=True).data,
                'clubs': AdminClubSerializer(Club.objects.select_related('created_by').annotate(
                    member_count=Count('memberships')).order_by('-created_at')[:5], many=True).data,
                'reports': AdminReportSerializer(Report.objects.select_related('reported_by', 'resolved_by', 'content_type')[:5], many=True).data,
            },
        })


class AdminUserListView(AdminListAPIView):
    serializer_class = AdminUserSerializer
    search_fields = ['email', 'name']
    ordering_fields = ['date_joined', 'email', 'name']

    def get_queryset(self):
        queryset = user_queryset()
        state = self.request.query_params.get('status')
        role = self.request.query_params.get('role')
        if state in {'active', 'inactive'}:
            queryset = queryset.filter(is_active=state == 'active')
        if role == 'admin':
            queryset = queryset.filter(Q(is_staff=True) | Q(is_superuser=True) | Q(groups__name='Administrators')).distinct()
        elif role == 'user':
            queryset = queryset.filter(is_staff=False, is_superuser=False).exclude(groups__name='Administrators')
        return queryset


class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsPlatformAdmin]
    serializer_class = AdminUserSerializer

    def get_queryset(self):
        return user_queryset()

    def _ensure_not_last_superuser(self, user):
        if user.is_superuser and User.objects.filter(is_superuser=True).count() <= 1:
            raise ValidationError({'detail': 'The last superuser cannot be removed or deactivated.'})

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        self._ensure_not_last_superuser(user)  # check superuser guard first
        if user == request.user:
            return Response({'detail': 'You cannot delete your own account.'}, status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)


class AdminUserStatusView(APIView):
    permission_classes = [IsPlatformAdmin]

    def patch(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        active = request.data.get('is_active')
        if not isinstance(active, bool):
            return Response({'is_active': 'This field must be a boolean.'}, status=status.HTTP_400_BAD_REQUEST)
        if not active and user.is_superuser and User.objects.filter(is_superuser=True).count() <= 1:
            return Response({'detail': 'The last superuser cannot be deactivated.'}, status=status.HTTP_400_BAD_REQUEST)
        if not active and user == request.user:
            return Response({'detail': 'You cannot deactivate your own account.'}, status=status.HTTP_400_BAD_REQUEST)
        user.is_active = active
        user.save(update_fields=['is_active'])
        return Response(AdminUserSerializer(user_queryset().get(pk=user.pk)).data)


class AdminClubListView(AdminListAPIView):
    serializer_class = AdminClubSerializer
    search_fields = ['name', 'description', 'genre', 'created_by__email']
    ordering_fields = ['name', 'created_at']

    def get_queryset(self):
        queryset = Club.objects.select_related('created_by').prefetch_related('memberships__user').annotate(member_count=Count('memberships'))
        if state := self.request.query_params.get('status'):
            queryset = queryset.filter(status=state.upper())
        if genre := self.request.query_params.get('genre'):
            queryset = queryset.filter(genre__iexact=genre)
        return queryset.order_by('name')


class AdminClubDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsPlatformAdmin]
    serializer_class = AdminClubSerializer
    queryset = Club.objects.select_related('created_by').prefetch_related('memberships__user').annotate(member_count=Count('memberships'))


class AdminClubStatusView(APIView):
    permission_classes = [IsPlatformAdmin]

    def patch(self, request, pk):
        try:
            club = Club.objects.get(pk=pk)
        except Club.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        value = request.data.get('status', '').upper()
        if value not in Club.Status.values:
            return Response({'status': f'Must be one of: {", ".join(Club.Status.values)}.'}, status=status.HTTP_400_BAD_REQUEST)
        club.status = value
        club.save(update_fields=['status'])
        refreshed = Club.objects.select_related('created_by').prefetch_related('memberships__user').annotate(
            member_count=Count('memberships')).get(pk=club.pk)
        return Response(AdminClubSerializer(refreshed).data)


class AdminPostListView(AdminListAPIView):
    serializer_class = AdminPostSerializer
    search_fields = ['movie_title', 'body', 'user__email', 'user__name']
    ordering_fields = ['created_at', 'updated_at', 'movie_title']

    def get_queryset(self):
        queryset = Post.objects.select_related('user').annotate(like_count=Count('likes', distinct=True), comment_count=Count('comments', distinct=True))
        if state := self.request.query_params.get('status'):
            queryset = queryset.filter(status=state.upper())
        return queryset.order_by('-created_at')


class AdminMovieListView(AdminListAPIView):
    serializer_class = AdminMovieSerializer
    search_fields = ['movie_title']
    ordering_fields = ['movie_id', 'movie_title', 'review_count']

    def get_queryset(self):
        queryset = Post.objects.values('movie_id', 'movie_title').annotate(
            review_count=Count('id', filter=Q(stars__isnull=False)),
        )
        return queryset.order_by('-review_count', 'movie_title')


class AdminPostDetailView(generics.RetrieveAPIView):
    permission_classes = [IsPlatformAdmin]
    serializer_class = AdminPostSerializer
    queryset = Post.objects.select_related('user').annotate(like_count=Count('likes', distinct=True), comment_count=Count('comments', distinct=True))


class AdminPostModerateView(APIView):
    permission_classes = [IsPlatformAdmin]

    def patch(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        value = request.data.get('status', '').upper()
        if value not in Post.ModerationStatus.values:
            return Response({'status': f'Must be one of: {", ".join(Post.ModerationStatus.values)}.'}, status=status.HTTP_400_BAD_REQUEST)
        post.status = value
        post.save(update_fields=['status', 'updated_at'])
        refreshed = Post.objects.select_related('user').annotate(
            like_count=Count('likes', distinct=True), comment_count=Count('comments', distinct=True)).get(pk=post.pk)
        return Response(AdminPostSerializer(refreshed).data)


class AdminPostDeleteView(generics.DestroyAPIView):
    permission_classes = [IsPlatformAdmin]
    queryset = Post.objects.all()


class AdminReviewDeleteView(AdminPostDeleteView):
    queryset = Post.objects.filter(stars__isnull=False)


class AdminCommentListView(AdminListAPIView):
    serializer_class = AdminCommentSerializer
    search_fields = ['body', 'user__email', 'user__name', 'post__movie_title']
    ordering_fields = ['created_at']

    def get_queryset(self):
        queryset = Comment.objects.select_related('user', 'post')
        if state := self.request.query_params.get('status'):
            queryset = queryset.filter(status=state.upper())
        return queryset


class AdminCommentModerateView(APIView):
    permission_classes = [IsPlatformAdmin]

    def patch(self, request, pk):
        try:
            comment = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        value = request.data.get('status', '').upper()
        if value not in Comment.ModerationStatus.values:
            return Response({'status': f'Must be one of: {", ".join(Comment.ModerationStatus.values)}.'}, status=status.HTTP_400_BAD_REQUEST)
        comment.status = value
        comment.save(update_fields=['status'])
        return Response(AdminCommentSerializer(comment).data)


class AdminCommentDeleteView(generics.DestroyAPIView):
    permission_classes = [IsPlatformAdmin]
    queryset = Comment.objects.all()


class AdminReviewListView(AdminPostListView):
    def get_queryset(self):
        return super().get_queryset().filter(stars__isnull=False)


class AdminActivityListView(AdminListAPIView):
    serializer_class = ActivityLogSerializer
    search_fields = ['movie_title', 'actor__email', 'actor__name']
    ordering_fields = ['created_at', 'event_type']

    def get_queryset(self):
        queryset = ActivityLog.objects.select_related('actor', 'review')
        if event_type := self.request.query_params.get('event_type'):
            queryset = queryset.filter(event_type=event_type.upper())
        return queryset


class AdminReportListView(AdminListAPIView):
    serializer_class = AdminReportSerializer
    search_fields = ['reason', 'description', 'reported_by__email']
    ordering_fields = ['created_at', 'status']

    def get_queryset(self):
        queryset = Report.objects.select_related('reported_by', 'resolved_by', 'content_type')
        if state := self.request.query_params.get('status'):
            queryset = queryset.filter(status=state.upper())
        if target_type := self.request.query_params.get('type'):
            queryset = queryset.filter(content_type__model=target_type.lower())
        return queryset


class AdminReportDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsPlatformAdmin]
    serializer_class = AdminReportSerializer
    queryset = Report.objects.select_related('reported_by', 'resolved_by', 'content_type')

    def perform_update(self, serializer):
        report = serializer.save()
        if report.status in {Report.Status.RESOLVED, Report.Status.DISMISSED}:
            report.resolved_at = timezone.now()
            report.resolved_by = self.request.user
            report.save(update_fields=['resolved_at', 'resolved_by'])


class AnalyticsView(APIView):
    permission_classes = [IsPlatformAdmin]

    @staticmethod
    def _daily(queryset, field):
        return list(queryset.annotate(date=TruncDate(field)).values('date').annotate(count=Count('id')).order_by('date'))

    def get(self, request):
        return Response({
            'users_registered': self._daily(User.objects.all(), 'date_joined'),
            'posts_created': self._daily(Post.objects.all(), 'created_at'),
            'clubs_created': self._daily(Club.objects.all(), 'created_at'),
            'most_popular_genres': list(Club.objects.exclude(genre='').values('genre').annotate(count=Count('id')).order_by('-count', 'genre')[:10]),
            'most_active_clubs': list(Club.objects.annotate(member_count=Count('memberships')).values('id', 'name', 'member_count').order_by('-member_count', 'name')[:10]),
            'most_reviewed_movies': list(Post.objects.filter(stars__isnull=False).values('movie_id', 'movie_title').annotate(review_count=Count('id')).order_by('-review_count', 'movie_title')[:10]),
            'most_active_users': list(User.objects.annotate(post_count=Count('posts', distinct=True), comment_count=Count('comments', distinct=True)).values('id', 'name', 'email', 'post_count', 'comment_count').order_by('-post_count', '-comment_count', 'email')[:10]),
        })
