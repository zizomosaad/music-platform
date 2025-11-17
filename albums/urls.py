from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AlbumViewSet,
    CreateAlbumViewSet,
    AlbumDetailView,
    AddSongView,
    SongDetailView,
)

router = DefaultRouter()
router.register("albums", AlbumViewSet, basename="album")
router.register("albums/manage", CreateAlbumViewSet, basename="create-album")

urlpatterns = [
    path("", include(router.urls)),
    path("albums/<int:pk>/", AlbumDetailView.as_view(), name="album-detail"),
    path("albums/<int:pk>/songs/add/", AddSongView.as_view(), name="album-add-song"),
    path("songs/<int:pk>/", SongDetailView.as_view(), name="song-detail"),
] 
