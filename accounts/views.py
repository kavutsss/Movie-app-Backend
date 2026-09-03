from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema

from administration.models import ActivityLog
from administration.services import log_activity
from .serializers import RegisterSerializer, UserSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
	queryset = User.objects.all()
	serializer_class = RegisterSerializer
	permission_classes = [permissions.AllowAny]


class UserListView(generics.ListAPIView):
	queryset = User.objects.all()
	serializer_class = UserSerializer
	permission_classes = [permissions.AllowAny]


class LogoutView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	@extend_schema(responses=OpenApiTypes.OBJECT)
	def post(self, request):
		log_activity(request, ActivityLog.EventType.LOGOUT)
		return Response({'detail': 'Logout successful. Discard the JWT tokens on the client.'})


class AuthApiView(APIView):
	permission_classes = [permissions.AllowAny]

	@extend_schema(responses=OpenApiTypes.OBJECT)
	def get(self, request):
		return Response({
			'register': '/api/auth/register/',
			'login': '/api/auth/login/',
			'token_refresh': '/api/auth/token/refresh/',
			'logout': '/api/auth/logout/',
		})


class UserDetailView(generics.RetrieveUpdateAPIView):
	queryset = User.objects.all()
	serializer_class = UserSerializer

	def get_permissions(self):
		return [permissions.AllowAny()] if self.request.method == 'GET' else [permissions.IsAuthenticated()]

	def update(self, request, *args, **kwargs):
		if request.user.pk != self.get_object().pk:
			return Response({'detail': 'You can only edit your own profile.'}, status=status.HTTP_403_FORBIDDEN)
		return super().update(request, *args, **kwargs)


class FollowView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	@extend_schema(responses=OpenApiTypes.OBJECT)
	def post(self, request, pk):
		target = generics.get_object_or_404(User, pk=pk)
		if target == request.user:
			return Response({'detail': 'You cannot follow yourself.'}, status=status.HTTP_400_BAD_REQUEST)
		request.user.following.add(target)
		return Response({'following': True})

	@extend_schema(responses=None)
	def delete(self, request, pk):
		target = generics.get_object_or_404(User, pk=pk)
		request.user.following.remove(target)
		return Response(status=status.HTTP_204_NO_CONTENT)
