from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from administration.models import ActivityLog
from administration.services import log_activity
from .models import Club, ClubMember
from .serializers import ClubMemberSerializer, ClubSerializer


class ClubListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Club.objects.select_related('created_by').prefetch_related('memberships')
    serializer_class = ClubSerializer

    def perform_create(self, serializer):
        club = serializer.save(created_by=self.request.user)
        ClubMember.objects.create(club=club, user=self.request.user)
        log_activity(self.request, ActivityLog.EventType.CLUB_CREATED,
            metadata={'club_id': club.pk, 'club_name': club.name})


class ClubDetailView(generics.RetrieveDestroyAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Club.objects.all()
    serializer_class = ClubSerializer

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.created_by != request.user and not request.user.is_staff:
            return Response({'detail': 'Only the club owner can delete it.'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


class ClubMembershipView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=ClubMemberSerializer)
    def post(self, request, pk):
        club = generics.get_object_or_404(Club, pk=pk)
        membership, created = ClubMember.objects.get_or_create(club=club, user=request.user)
        if created:
            log_activity(request, ActivityLog.EventType.CLUB_JOINED,
                metadata={'club_id': club.pk, 'club_name': club.name})
        return Response(ClubMemberSerializer(membership).data, status=status.HTTP_201_CREATED)

    @extend_schema(responses=None)
    def delete(self, request, pk):
        membership = generics.get_object_or_404(ClubMember, club_id=pk, user=request.user)
        membership.delete()
        log_activity(request, ActivityLog.EventType.CLUB_LEFT,
            metadata={'club_id': pk, 'club_name': membership.club.name})
        return Response(status=status.HTTP_204_NO_CONTENT)
