from rest_framework import serializers
from django.contrib.auth import password_validation
from apps.common.models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer for the CustomUser model.
    Handles serialization and deserialization of user data.
    """

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "password",
            "first_name",
            "last_name",
            "email",
            "profile_picture",
        ]
        # Extra keyword arguments for specific fields
        extra_kwargs = {
            "password": {
                "write_only": True
            },  # Ensure password is only used for writing (creation/update)
            "email": {"required": True},
            "id": {"read_only": True},
        }

    def validate_password(self, password):
        password_validation.validate_password(password)
        return password

    # Example of creating a user with a hashed password
    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = CustomUser.objects.create_user(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    # Example of updating a user, handling password separately if provided
    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user


class ProfilePictureSerializer(serializers.ModelSerializer):
    """
    Serializer specifically for updating the profile picture.
    """

    class Meta:
        model = CustomUser
        fields = ["profile_picture"]
