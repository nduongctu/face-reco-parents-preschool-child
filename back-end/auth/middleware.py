from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException
from jose import JWTError, jwt
from datetime import datetime
from config import settings

class TokenExpiryMiddleware(BaseHTTPMiddleware):
    @staticmethod
    async def dispatch(request: Request, call_next):
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
                expire = payload.get("exp")
                if expire and datetime.utcfromtimestamp(expire) < datetime.utcnow():
                    raise HTTPException(status_code=401, detail="Token đã hết hạn")
            except JWTError:
                raise HTTPException(status_code=401, detail="Token không hợp lệ")
        response = await call_next(request)
        return response
