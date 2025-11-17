from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
from .models import Artist
from albums.models import Albums, Song
from albums.serializer import AlbumSerializer, SongsSerializer


class ArtistSerializer(ModelSerializer):
    albums = AlbumSerializer(
        many=True,
    )
    # Write album IDs

    def _get_or_create_albums(self, albums, artist):
        """Handle getting or creating tags as needed"""
        for album in albums:
            album_obj, created = Albums.objects.get_or_create(**album)
            album_obj.artist = artist
            album_obj.save()

    class Meta:
        model = Artist
        fields = ["id", "stage_name", "social_link", "albums"]

    def create(self, validated_data):
        """Create an artist."""
        albums_data = validated_data.pop("albums", [])
        artist = Artist.objects.create(**validated_data)

        if albums_data:
            self._get_or_create_albums(albums_data, artist)

        return artist

    def update(self, instance, validated_data):
        albums_data = validated_data.pop("albums", None)
        if albums_data is not None:
            self._get_or_create_albums(albums_data, instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    