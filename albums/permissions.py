from rest_framework import permissions
from .models import Albums, Song
from artists.models import Artist


def _artist_user_from_obj(obj):
    # obj may be Albums or Song
    artist = getattr(obj, "artist", None)
    if artist is not None:
        return getattr(artist, "user", None)
    album = getattr(obj, "album", None)
    if album is not None:
        return getattr(getattr(album, "artist", None), "user", None)
    return None


class IsArtist(permissions.BasePermission):
    """
    Allow creation only for authenticated users that have an Artist record.
    Safe methods allowed for everyone.
    """

    message = "Only users who are artists can perform this action."

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        return Artist.objects.filter(user=user).exists()


class IsAdminOrArtistOwner(permissions.BasePermission):
    """
    Allow SAFE methods to anyone.
    For unsafe methods, allow only admins or the user who owns the artist related to the object.
    Works with Albums and Song instances.
    """

    message = "Only admins or the artist owner can modify this object."

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        if user.is_staff:
            return True
        owner = _artist_user_from_obj(obj)
        return bool(owner and owner == user)
