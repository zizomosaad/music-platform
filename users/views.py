from django.contrib.auth import get_user_model
from rest_framework import mixins, generics, viewsets, permissions
from .serializers import CreateUserSerializer, ManageUserSerializer


User = get_user_model()


class CreateUserView(mixins.CreateModelMixin, generics.GenericAPIView):
    serializer_class = CreateUserSerializer
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.none()  # not used but GenericAPIView expects it

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class CurrentUserView(mixins.RetrieveModelMixin, generics.GenericAPIView):
    serializer_class = ManageUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class UsersViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    Admin-only: list all users and retrieve specific user by pk.
    """
    serializer_class = ManageUserSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all()
