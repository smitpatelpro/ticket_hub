from channels.auth import AuthMiddlewareStack
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections
from django.conf import settings
from urllib.parse import parse_qs
from channels.db import database_sync_to_async

from apps.common.models import CustomUser


class JwtAuthMiddleware:
    """
    Custom middleware to authenticate users based on a JWT token
    passed as a query parameter in the WebSocket connection.
    """

    def __init__(self, inner):
        # Store the next middleware or consumer in the stack
        self.inner = inner

    # Corrected __call__ method signature to accept scope, receive, and send
    async def __call__(self, scope, receive, send):
        # This method is called for each incoming connection.

        # Close old database connections to prevent issues with async code
        # and long-lived connections.
        close_old_connections()

        # Get the query string from the scope. It's a byte string.
        query_string = scope['query_string'].decode()

        # Parse the query string into a dictionary
        # parse_qs returns a dictionary where values are lists, so we get the first item
        query_parameters = parse_qs(query_string)

        # Get the token from the query parameters.
        # We expect it to be named 'token' in the URL (e.g., ws://.../?token=<your_jwt_token>)
        # Use .get() with a default of [None] to safely get the first value or None
        token = query_parameters.get('token', [None])[0]

        # Initialize the user to AnonymousUser
        scope['user'] = AnonymousUser()

        if token:
            try:
                # Validate the token using Simple JWT's AccessToken
                # This will raise an exception if the token is invalid or expired
                access_token = AccessToken(token)

                # Get the user ID from the token's claims.
                # Simple JWT's default claim for user ID is 'user_id'.
                user_id = access_token['user_id']

                # Fetch the user from the database using the user ID from the token.
                # Use the CustomUser model defined in settings.AUTH_USER_MODEL.
                user = await database_sync_to_async(CustomUser.objects.get)(id=user_id) # Use async for DB access

                # If the user is found, attach the user object to the scope.
                scope['user'] = user

            except Exception as e:
                # Handle various exceptions during token validation or user lookup:
                # - InvalidToken (from rest_framework_simplejwt)
                # - CustomUser.DoesNotExist (if user_id in token doesn't exist)
                # - KeyError (if 'user_id' claim is missing)
                print(f"JWT authentication failed in Channels middleware: {e}")
                # Keep user as AnonymousUser if authentication fails

        # Call the next middleware or the consumer in the stack.
        # The scope, now potentially with an authenticated user, is passed along.
        # Pass receive and send along as well.
        return await self.inner(scope, receive, send) # Pass receive and send here

# Stack the custom middleware with Django's AuthMiddlewareStack.
# AuthMiddlewareStack provides the 'user' attribute in the scope and handles
# session authentication if needed (though less common with JWT-only APIs).
# Placing JwtAuthMiddleware *before* AuthMiddlewareStack ensures our JWT logic runs first.
# The lambda function makes it a factory for the middleware stack.
JwtAuthMiddlewareStack = lambda inner: JwtAuthMiddleware(AuthMiddlewareStack(inner))
