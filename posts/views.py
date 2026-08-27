from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Comment, Post
from .serializers import CommentSerializer, PostSerializer


class PostListCreateView(generics.ListCreateAPIView):
	queryset = Post.objects.select_related('user').prefetch_related('likes', 'comments__user')
	serializer_class = PostSerializer

	def perform_create(self, serializer):
		serializer.save(user=self.request.user)


class PostDetailView(generics.RetrieveDestroyAPIView):
	queryset = Post.objects.all()
	serializer_class = PostSerializer

	def destroy(self, request, *args, **kwargs):
		if self.get_object().user != request.user:
			return Response({'detail': 'Only the post owner can delete it.'}, status=status.HTTP_403_FORBIDDEN)
		return super().destroy(request, *args, **kwargs)


class LikeView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def post(self, request, pk):
		post = generics.get_object_or_404(Post, pk=pk)
		post.likes.add(request.user)
		return Response({'liked': True, 'like_count': post.likes.count()})

	def delete(self, request, pk):
		post = generics.get_object_or_404(Post, pk=pk)
		post.likes.remove(request.user)
		return Response({'liked': False, 'like_count': post.likes.count()})


class CommentListCreateView(generics.ListCreateAPIView):
	serializer_class = CommentSerializer

	def get_queryset(self):
		return Comment.objects.filter(post_id=self.kwargs['pk']).select_related('user')

	def perform_create(self, serializer):
		serializer.save(post_id=self.kwargs['pk'], user=self.request.user)


class CommentDeleteView(generics.DestroyAPIView):
	queryset = Comment.objects.all()
	serializer_class = CommentSerializer

	def destroy(self, request, *args, **kwargs):
		if self.get_object().user != request.user:
			return Response({'detail': 'Only the comment owner can delete it.'}, status=status.HTTP_403_FORBIDDEN)
		return super().destroy(request, *args, **kwargs)