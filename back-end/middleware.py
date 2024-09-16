from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from jose import JWTError, jwt
from config import settings
from datetime import datetime

class TokenExpiryMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = request.headers.get("Authorization")
        if token and token.startswith("Bearer "):
            token = token[len("Bearer "):]
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
                exp = payload.get("exp")
                if datetime.utcnow() > datetime.fromtimestamp(exp):
                    return Response("Token đã hết hạn", status_code=401)
            except JWTError:
                return Response("Token không hợp lệ", status_code=401)
        return await call_next(request)