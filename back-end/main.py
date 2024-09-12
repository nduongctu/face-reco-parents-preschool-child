from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from login import router as auth_router
from admin import router as admin_router
from middleware import TokenExpiryMiddleware

# Tạo đối tượng FastAPI
app = FastAPI()

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cấu hình Middleware
app.add_middleware(TokenExpiryMiddleware)

# Đăng ký các router
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])

# Dependency để cung cấp kết nối với cơ sở dữ liệu
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Chạy ứng dụng FastAPI
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
