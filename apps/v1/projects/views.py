from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.contrib.auth.models import User

class HelloView(APIView):
    """
    A simple API view that returns a hello message.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, version="v1", format=None):
        """
        Return hello message.
        """

        return Response({"message": "Hello, World!"})