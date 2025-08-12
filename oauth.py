import os
import httpx
from jose import jwt, JWTError
from fastmcp.server.middleware import Middleware, MiddlewareContext
from dotenv import load_dotenv

load_dotenv()

OAUTH_DOMAIN = os.getenv("OAUTH_DOMAIN")
OAUTH_AUDIENCE = os.getenv("OAUTH_AUDIENCE")
ALGORITHMS = os.getenv("OAUTH_AUDIENCE")

class OAuthMiddleware(Middleware):
    async def on_tool_call(self, ctx: MiddlewareContext, next_call):
        auth_header = ctx.request_headers.get("authorization")
        if not auth_header or not auth_header.lower().startswith("bearer "):
            raise PermissionError("Missing or invalid Authorization header")

        token = auth_header.split(" ")[1]
        try:
            jwks_url = f"https://{OAUTH_DOMAIN}/.well-known/jwks.json"
            async with httpx.AsyncClient() as client:
                jwks = (await client.get(jwks_url)).json()

            unverified_header = jwt.get_unverified_header(token)
            rsa_key = next(
                (key for key in jwks["keys"] if key["kid"] == unverified_header["kid"]),
                None
            )
            if not rsa_key:
                raise PermissionError("No matching JWKS key found")

            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=[ALGORITHMS],
                audience=OAUTH_AUDIENCE,
                issuer=f"https://{OAUTH_DOMAIN}/",
            )
            ctx.state["user"] = payload  # Store claims for tools to use
        except JWTError as e:
            raise PermissionError(f"Token validation error: {e}")

        return await next_call(ctx)
