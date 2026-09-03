from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from administration.models import ActivityLog
from administration.services import log_activity

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'bio', 'avatar', 'date_joined']
        read_only_fields = ['id', 'email', 'date_joined']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['name', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        request = self.context.get('request')
        if request:
            log_activity(request, ActivityLog.EventType.REGISTER, actor=user)
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        is_admin = (
            user.is_staff or
            user.is_superuser or
            user.groups.filter(name='Administrators').exists()
        )
        data['user'] = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'role': 'superuser' if user.is_superuser else ('admin' if is_admin else 'user'),
        }
        return data