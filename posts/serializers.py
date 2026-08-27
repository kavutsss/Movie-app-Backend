from rest_framework import serializers

from .models import Comment, Post


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'body', 'created_at']
        read_only_fields = ['id', 'post', 'user', 'created_at']


class PostSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    like_count = serializers.IntegerField(source='likes.count', read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'user', 'movie_id', 'movie_title', 'body', 'stars', 'like_count', 'comments', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'like_count', 'comments', 'created_at', 'updated_at']

    def validate_stars(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError('Stars must be between 1 and 5.')
        return value