from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Club, ClubMember
from .serializers import ClubMemberSerializer, ClubSerializer


class ClubListCreateView(generics.ListCreateAPIView):
    queryset = Club.objects.select_related('created_by').prefetch_related('memberships')
    serializer_class = ClubSerializer

    def perform_create(self, serializer):
        club = serializer.save(created_by=self.request.user)
        ClubMember.objects.create(club=club, user=self.request.user)


class ClubDetailView(generics.RetrieveDestroyAPIView):
    queryset = Club.objects.all()
    serializer_class = ClubSerializer

    def destroy(self, request, *args, **kwargs):
        if self.get_object().created_by != request.user:
            return Response({'detail': 'Only the club owner can delete it.'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


class ClubMembershipView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        club = generics.get_object_or_404(Club, pk=pk)
        membership, _ = ClubMember.objects.get_or_create(club=club, user=request.user)
        return Response(ClubMemberSerializer(membership).data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        membership = generics.get_object_or_404(ClubMember, club_id=pk, user=request.user)
        membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

from rest_framework import generics, permissions

from .models import Watchlist
from .serializers import WatchlistSerializer


class WatchlistListCreateView(generics.ListCreateAPIView):
    serializer_class = WatchlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WatchlistDetailView(generics.DestroyAPIView):
    serializer_class = WatchlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user)
