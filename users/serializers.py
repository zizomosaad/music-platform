from rest_framework import serializers
from users.models import User
from rest_framework.validators import UniqueValidator
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from django.db import IntegrityError, transaction
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError


class CreateUserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True, required=True, min_length=8)
    password2 = serializers.CharField(write_only=True, required=True, min_length=8)
    username = serializers.CharField(required=True)
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="A user with that email already exists.",
            )
        ],
    )

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "password1",
            "password2",
            "first_name",
            "last_name",
        )

    def validate_username(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError(
                "Username is required and cannot be blank."
            )
        return value

    def validate(self, attrs):
        # check passwords match
        p1 = attrs.get("password1")
        p2 = attrs.get("password2")
        if p1 != p2:
            raise serializers.ValidationError({"password2": "Passwords do not match."})

        # optional: run Django password validators
        try:
            validate_password(p1)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password1": list(exc.messages)})

        return attrs

    def create(self, validated_data):

        password = validated_data.pop("password1")
        validated_data.pop("password2")
        try:
            with transaction.atomic():
                user = User(**validated_data)
                user.set_password(password)
                user.save()
                return user
        except IntegrityError as e:
            # inspect DB to return an accurate field error (avoid relying on DB message text)
            if User.objects.filter(email=validated_data.get("email")).exists():
                raise serializers.ValidationError(
                    {"email": "A user with that email already exists."}
                )
            if User.objects.filter(username=validated_data.get("username")).exists():
                raise serializers.ValidationError(
                    {"username": "A user with that username already exists."}
                )
            # fallback: return generic error and include original message for debugging
            raise serializers.ValidationError(
                {"non_field_errors": ["Database error: " + str(e)]}
            )


class ManageUserSerializer(serializers.ModelSerializer):
    """Serializer for retrieving/updating user data (safe fields only)."""

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
        )
        read_only_fields = ("id", "is_staff", "is_active")
