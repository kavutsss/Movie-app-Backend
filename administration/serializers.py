from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from rest_framework import serializers

from clubs.models import Club, ClubMember
from posts.models import Comment, Post, Report
from .models import ActivityLog

User = get_user_model()


class ActivityLogSerializer(serializers.ModelSerializer):
    actor = serializers.StringRelatedField()
    actor_email = serializers.EmailField(source='actor.email', read_only=True, allow_null=True)
    event = serializers.CharField(source='get_event_type_display', read_only=True)

    class Meta:
        model = ActivityLog
        fields = ['id', 'actor', 'actor_email', 'event_type', 'event', 'movie_id', 'movie_title', 'review',
                  'ip_address', 'metadata', 'created_at']


class AdminMovieSerializer(serializers.Serializer):
    movie_id = serializers.IntegerField()
    movie_title = serializers.CharField()
    review_count = serializers.IntegerField()


class AdminUserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    post_count = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    club_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'bio', 'avatar', 'is_active',
                  'role', 'date_joined', 'last_login', 'post_count', 'comment_count', 'club_count']
        read_only_fields = ['id', 'email', 'is_active', 'role', 'date_joined',
                            'last_login', 'post_count', 'comment_count', 'club_count']

    def get_role(self, obj):
        if obj.is_superuser:
            return 'superuser'
        if obj.is_staff or obj.groups.filter(name='Administrators').exists():
            return 'admin'
        return 'user'


class AdminClubSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    member_count = serializers.IntegerField(read_only=True)
    members = serializers.SerializerMethodField()

    class Meta:
        model = Club
        fields = ['id', 'name', 'description', 'genre', 'status', 'created_by', 'member_count', 'members', 'created_at']
        read_only_fields = ['id', 'created_by', 'member_count', 'members', 'created_at']

    def get_members(self, obj):
        memberships = list(obj.memberships.all())[:50]  # uses prefetch cache, sliced in Python
        return [{'id': m.user_id, 'name': m.user.name, 'email': m.user.email, 'joined_at': m.joined_at}
                for m in memberships]


class AdminPostSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'user', 'movie_id', 'movie_title', 'body', 'stars', 'status', 'like_count', 'comment_count',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'like_count', 'comment_count', 'created_at', 'updated_at']


class AdminCommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    post_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'post_id', 'user', 'body', 'status', 'created_at']
        read_only_fields = ['id', 'post_id', 'user', 'created_at']


class AdminReportSerializer(serializers.ModelSerializer):
    reported_by = serializers.StringRelatedField(read_only=True)
    resolved_by = serializers.StringRelatedField(read_only=True)
    target_type = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = ['id', 'reported_by', 'content_type', 'object_id', 'target_type', 'reason', 'description', 'status',
                  'created_at', 'resolved_at', 'resolved_by']
        read_only_fields = ['id', 'reported_by', 'target_type', 'created_at', 'resolved_at', 'resolved_by']

    def get_target_type(self, obj):
        return obj.content_type.model
