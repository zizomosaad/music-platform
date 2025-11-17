from django.db import models

from django.db.models import Count, Q
from users.models import User

# Create your models here.


class ArtistManager(models.Manager):
    def get_queryset(self):
        # annotate every queryset with the count of approved albums
        return (
            super()
            .get_queryset()
            .annotate(
                approved_albums=Count("albums", filter=Q(albums__isApproved=True))
            )
        )


class Artist(models.Model):
    stage_name = models.CharField(max_length=100, unique=True, null=False, blank=False)
    social_link = models.URLField(max_length=200, blank=True)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="artist_profile",
        null=True,
    )

    objects = ArtistManager()

    class Meta:
        ordering = ["stage_name"]

    def __str__(self):
        return self.stage_name
