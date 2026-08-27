from rest_framework import serializers

from .models import Club, ClubMember


class ClubSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    member_count = serializers.IntegerField(source='memberships.count', read_only=True)

    class Meta:
        model = Club
        fields = ['id', 'name', 'description', 'genre', 'created_by', 'member_count', 'created_at']
        read_only_fields = ['id', 'created_by', 'member_count', 'created_at']


class ClubMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClubMember
        fields = ['id', 'club', 'user', 'joined_at']
        read_only_fields = ['id', 'club', 'user', 'joined_at']