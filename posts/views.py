from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema

from administration.models import ActivityLog
from administration.services import log_activity
from .models import Comment, Post
from .serializers import CommentSerializer, PostSerializer


class PostListCreateView(generics.ListCreateAPIView):
	queryset = Post.objects.filter(status=Post.ModerationStatus.VISIBLE).select_related('user').prefetch_related('likes', 'comments__user')
	serializer_class = PostSerializer

	def perform_create(self, serializer):
		post = serializer.save(user=self.request.user)
		if post.stars is not None:
			log_activity(self.request, ActivityLog.EventType.REVIEW_CREATED,
				movie_id=post.movie_id, movie_title=post.movie_title, review=post)


class PostDetailView(generics.RetrieveDestroyAPIView):
	queryset = Post.objects.filter(status=Post.ModerationStatus.VISIBLE)
	serializer_class = PostSerializer

	def destroy(self, request, *args, **kwargs):
		obj = self.get_object()
		if obj.user != request.user and not request.user.is_staff:
			return Response({'detail': 'Only the post owner can delete it.'}, status=status.HTTP_403_FORBIDDEN)
		return super().destroy(request, *args, **kwargs)


class LikeView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	@extend_schema(responses=OpenApiTypes.OBJECT)
	def post(self, request, pk):
		post = generics.get_object_or_404(Post, pk=pk)
		post.likes.add(request.user)
		log_activity(request, ActivityLog.EventType.LIKE_ADDED, movie_id=post.movie_id,
			movie_title=post.movie_title, metadata={'post_id': post.pk})
		return Response({'liked': True, 'like_count': post.likes.count()})

	@extend_schema(responses=OpenApiTypes.OBJECT)
	def delete(self, request, pk):
		post = generics.get_object_or_404(Post, pk=pk)
		post.likes.remove(request.user)
		log_activity(request, ActivityLog.EventType.LIKE_REMOVED, movie_id=post.movie_id,
			movie_title=post.movie_title, metadata={'post_id': post.pk})
		return Response({'liked': False, 'like_count': post.likes.count()})


class MovieCheckView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def post(self, request, movie_id):
		log_activity(
			request,
			ActivityLog.EventType.MOVIE_CHECKED,
			movie_id=movie_id,
			movie_title=request.data.get('movie_title', ''),
		)
		return Response({'checked': True})


class CommentListCreateView(generics.ListCreateAPIView):
	serializer_class = CommentSerializer

	def get_queryset(self):
		return Comment.objects.filter(post_id=self.kwargs['pk'], status=Comment.ModerationStatus.VISIBLE).select_related('user')

	def perform_create(self, serializer):
		comment = serializer.save(post_id=self.kwargs['pk'], user=self.request.user)
		log_activity(self.request, ActivityLog.EventType.COMMENT_CREATED,
			movie_id=comment.post.movie_id, movie_title=comment.post.movie_title,
			metadata={'comment_id': comment.pk, 'post_id': comment.post_id})


class CommentDeleteView(generics.DestroyAPIView):
	queryset = Comment.objects.filter(status=Comment.ModerationStatus.VISIBLE)
	serializer_class = CommentSerializer

	def destroy(self, request, *args, **kwargs):
		if self.get_object().user != request.user:
			return Response({'detail': 'Only the comment owner can delete it.'}, status=status.HTTP_403_FORBIDDEN)
		return super().destroy(request, *args, **kwargs)
