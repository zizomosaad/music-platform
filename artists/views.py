from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, viewsets, mixins, permissions
from .models import Artist
from .serializers import ArtistSerializer


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Allow safe methods for authenticated users, but only allow updates/deletes
    if request.user is the artist.user (creator) or an admin (is_staff/is_superuser).
    """

    def has_object_permission(self, request, view, obj):
        # allow GET/HEAD/OPTIONS for authenticated users (the view already requires IsAuthenticated)
        if request.method in permissions.SAFE_METHODS:
            return True
        # for unsafe methods require owner or admin
        return bool(
            getattr(obj, "user", None) == request.user
            or request.user.is_staff
            or request.user.is_superuser
        )


class ArtistsViewSet(
    mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet
):

    permission_classes = [IsAuthenticated]
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ArtistDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View to retrieve, update, or delete an artist."""

    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    serializer_class = ArtistSerializer

    def get_queryset(self):
        qs = Artist.objects.all()
        if not self.request.user.is_staff and self.request.method in [
            "PUT",
            "PATCH",
            "DELETE",
        ]:
            qs = qs.filter(user=self.request.user)
        return qs
