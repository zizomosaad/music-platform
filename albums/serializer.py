from rest_framework import serializers
from .models import Albums, Song


class AddSongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = ["id", "name", "image", "audio", "album"]
        read_only_fields = ["id"]
        extra_kwargs = {
            "name": {"required": True},
            "image": {"required": True},
            "audio": {"required": True},
        }

    def validate_image(self, value):
        if value.content_type not in ["image/png", "image/jpg", "image/jpeg"]:
            raise serializers.ValidationError(
                "Unsupported image format. Allowed formats: png, jpg, jpeg"
            )
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError(
                "Image file size exceeds the limit of 5MB."
            )

        return value

    def validate_audio(self, value):
        if value.content_type not in ["audio/mpeg", "audio/wav"]:
            raise serializers.ValidationError(
                "Unsupported audio format. Allowed formats: mp3, wav"
            )
        if value.size > 20 * 1024 * 1024:
            raise serializers.ValidationError(
                "Audio file size exceeds the limit of 20MB."
            )

        return value

    def create(self, validated_data):
        """Create a song."""
        album = validated_data.pop("album", None)
        song = Song.objects.create(**validated_data)
        if album:
            album.songs.add(song)
        return song



class SongsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = ("id", "name", "image", "audio",)
        read_only_fields = ("id",)


class AlbumSerializer(serializers.ModelSerializer):
    songs_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Song.objects.all(), source="songs", required=False
    )
    artist = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Albums
        fields = ("id", "name", "release_date", "cost", "isApproved", "artist", "songs_ids")
        read_only_fields = ("id", "artist")

    def create(self, validated_data):
        """Create an album."""
        # Get songs from validated_data (already mapped from songs_ids)
        songs = validated_data.pop("songs", [])
        album = Albums.objects.create(**validated_data)

        # Set the songs directly - no need to filter as they're already Song instances
        if songs:
            album.songs.set(songs)
        return album

    def update(self, instance, validated_data):
        """Update album."""
        # Get songs from validated_data (already mapped from songs_ids)
        songs = validated_data.pop("songs", None)

        if songs is not None:
            instance.songs.set(songs)  # Sets songs

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class RetrieveAlbumSerializer(serializers.ModelSerializer):
    songs = SongsSerializer(many=True, read_only=True)
    artist = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Albums
        fields = ["id", "name", "release_date", "cost", "songs", "artist"]


class ApproveAlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Albums
        fields = []

    def update(self, instance, validated_data):
        instance.isApproved = True
        instance.save()
        return instance
