# app/middleware/auth_middleware.py

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError
import os


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Simple JWT authentication middleware.

    Adds:
        request.state.user_id
    """

    async def dispatch(self, request: Request, call_next):

        # Public routes
        public_routes = {
            "/",
            "/docs",
            "/redoc",
            "/openapi.json"
        }

        if request.url.path in public_routes:
            return await call_next(request)

        auth_header = request.headers.get(
            "Authorization"
        )

        if not auth_header:
            raise HTTPException(
                status_code=401,
                detail="Authorization header missing"
            )

        try:

            scheme, token = auth_header.split()

            if scheme.lower() != "bearer":
                raise HTTPException(
                    status_code=401,
                    detail="Invalid auth scheme"
                )

            payload = jwt.decode(
                token,
                os.getenv("JWT_SECRET"),
                algorithms=["HS256"]
            )

            request.state.user_id = payload.get(
                "user_id"
            )

        except JWTError:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        return await call_next(request)