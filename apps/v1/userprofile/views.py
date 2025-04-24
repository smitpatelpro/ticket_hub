from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.v1.userprofile.serializers import (
    CustomUserSerializer,
    ProfilePictureSerializer,
)


class UserCreateView(APIView):
    """
    API view to create a new user.
    """

    permission_classes = [AllowAny]  # Allow anyone to register

    def post(self, request, *args, **kwargs):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    """
    API view to retrieve and update the authenticated user's profile.
    This view requires authentication and allows the user to view and update their profile information.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        serializer = CustomUserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfilePicutreView(APIView):
    """
    API view to retrieve and update the authenticated user's profile.
    This view requires authentication and allows the user to view and update their profile information.
    This API gives relative URL asuming that the Frontend already knows the API base URL and to avoid hardcoding the URL.
    """

    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        serializer = ProfilePictureSerializer(
            request.user, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
