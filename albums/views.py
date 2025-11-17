from rest_framework import viewsets, mixins, generics, permissions, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination

from django_filters import rest_framework as filters

from .models import Albums, Artist, Song
from .serializer import AlbumSerializer, AddSongSerializer, SongsSerializer
from .permissions import IsArtist, IsAdminOrArtistOwner


class AlbumPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100


class AlbumFilter(filters.FilterSet):
    min_cost = filters.NumberFilter(field_name="cost", lookup_expr="gte")
    max_cost = filters.NumberFilter(field_name="cost", lookup_expr="lte")
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Albums
        fields = ["min_cost", "max_cost", "name"]


class AlbumViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Public listing of approved albums.
    """

    permission_classes = [AllowAny]
    serializer_class = AlbumSerializer
    queryset = Albums.objects.filter(isApproved=True).select_related("artist")
    pagination_class = AlbumPagination
    filterset_class = AlbumFilter
    filter_backends = (filters.DjangoFilterBackend,)


class CreateAlbumViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    Create album: only users who are artists can create. The album.artist is set
    from the creator's Artist record.
    """

    permission_classes = [IsAuthenticated, IsArtist]
    serializer_class = AlbumSerializer
    queryset = Albums.objects.all()

    def perform_create(self, serializer):
        # resolve Artist for current user
        artist = Artist.objects.filter(user=self.request.user).first()
        if not artist:
            # should not happen because IsArtist already checked, but guard anyway
            raise permissions.PermissionDenied("You are not registered as an artist.")
        serializer.save(artist=artist)


class AlbumDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve anyone. Update/Delete only admin or artist owner.
    """

    queryset = Albums.objects.all().select_related("artist__user")
    serializer_class = AlbumSerializer
    permission_classes = [IsAdminOrArtistOwner]


class AddSongView(generics.CreateAPIView):
    """
    Add a song to a specific album:
    POST /albums/<album_pk>/songs/add/ with song fields (image/audio/name).
    Only artists who own the album or admins can add (if you want only artist creators,
    change permission logic below).
    """

    serializer_class = AddSongSerializer
    permission_classes = [
        IsAuthenticated,
        IsArtist,
    ]  # IsArtist ensures the caller is an artist

    def get_album(self):
        pk = self.kwargs.get("pk")
        return generics.get_object_or_404(
            Albums.objects.select_related("artist__user"), pk=pk
        )

    def perform_create(self, serializer):
        album = self.get_album()
        user = self.request.user
        # allow create only if admin or album artist owner matches request.user
        if not (user.is_staff or (album.artist and album.artist.user == user)):
            raise permissions.PermissionDenied(
                "You are not allowed to add songs to this album."
            )
        serializer.save(album=album)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class SongDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve song is public. Update/Delete only admin or artist owner of the parent album.
    """

    queryset = Song.objects.all().select_related("album__artist__user")
    serializer_class = SongsSerializer
    permission_classes = [IsAdminOrArtistOwner]
