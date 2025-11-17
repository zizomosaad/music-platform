from django.db import models
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.utils.text import slugify
import os

from artists.models import Artist

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill


def song_image_upload_to(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    artist_slug = (
        slugify(instance.album.artist.stage_name)
        if getattr(instance, "album", None) and instance.album.artist.stage_name
        else "unknown-artist"
    )
    album_slug = (
        slugify(instance.album.name)
        if getattr(instance, "album", None) and instance.album.name
        else "unknown-album"
    )
    song_slug = (
        slugify(instance.name)
        if instance.name
        else slugify(os.path.splitext(filename)[0])
    )
    fname = f"{song_slug}{ext}"
    return f"songs/{artist_slug}/{album_slug}/{song_slug}/images/{fname}"


def song_audio_upload_to(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    artist_slug = (
        slugify(instance.album.artist.stage_name)
        if getattr(instance, "album", None) and instance.album.artist.stage_name
        else "unknown-artist"
    )
    album_slug = (
        slugify(instance.album.name)
        if getattr(instance, "album", None) and instance.album.name
        else "unknown-album"
    )
    song_slug = (
        slugify(instance.name)
        if instance.name
        else slugify(os.path.splitext(filename)[0])
    )
    fname = f"{song_slug}{ext}"
    return f"songs/{artist_slug}/{album_slug}/{song_slug}/audio/{fname}"


def validate_image_file_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = [".png", ".jpg", ".jpeg"]
    if not ext in valid_extensions:
        raise ValidationError("Unsupported file extension. Allowed: png, jpg, jpeg")


# Create your models here.
class Albums(models.Model):
    artist = models.ForeignKey(
        Artist, on_delete=models.CASCADE, related_name="albums", null=True, blank=True
    )
    name = models.CharField(max_length=200, default="New Album")
    created_at = models.DateTimeField(auto_now_add=True)
    release_date = models.DateTimeField(blank=False, null=False)
    cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, blank=False, null=False
    )
    isApproved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} by {self.artist}"


class Song(models.Model):
    album = models.ForeignKey(Albums, on_delete=models.CASCADE, related_name="songs")
    # avoid referencing album at import time; use a simple default or blank
    name = models.CharField(max_length=200, default="", blank=False)
    image = models.ImageField(
        upload_to=song_image_upload_to,
        null=False,
        validators=[validate_image_file_extension],
        help_text="Allowed formats: png , jpg , jpeg",
    )

    image_thumbnail = ImageSpecField(
        source="image",
        processors=[ResizeToFill(100, 100)],
        format="JPEG",
        options={"quality": 60},
    )
    audio = models.FileField(
        upload_to=song_audio_upload_to,
        null=False,
        validators=[FileExtensionValidator(allowed_extensions=["mp3", "wav"])],
        help_text="Allowed formats: mp3 , wav",
    )

    def __str__(self):
        return f"{self.name} by {self.album.artist.stage_name}"
