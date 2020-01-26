from django.db import close_old_connections
from rest_framework.authtoken.models import Token
from asgiref.sync import sync_to_async
from urllib.parse import parse_qs
import asyncio
from channels.middleware import BaseMiddleware

class AuthMiddlewareStack:

    def __init__(self, inner):
        """
        Middleware constructor - just takes inner application.
        """
        self.inner = inner

    def __call__(self, scope):
        # token_key = parse_qs(scope["query_string"].decode("utf8"))["token"][0]
        # # teste = sync_to_async(self.main())
        # await self.main()
        # # print(teste)
        # Close old database connections to prevent usage of timed out connections
        # close_old_connections()
        # await asyncio.sleep(1)

        # Return the inner application directly and let it run everything else
        return self.inner(dict(scope))