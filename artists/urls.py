from django.urls import path, include
from .views import ArtistsViewSet, ArtistDetailView

from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register("artists", ArtistsViewSet, basename="artists")

urlpatterns = [
    path("", include(router.urls)),
    path("artists/<int:pk>/", ArtistDetailView.as_view(), name="artist-detail"),
]
