from django.urls import path, include
from .views import CreateUserView, CurrentUserView, UsersViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("users", UsersViewSet, basename="users")

urlpatterns = [
    path("create/", CreateUserView.as_view(), name="user-create"),
    path(
        "me/",
        CurrentUserView.as_view(),
    ),
    path("", include(router.urls)),
]
