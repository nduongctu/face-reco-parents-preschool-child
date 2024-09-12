from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models import TaiKhoan
from config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import redis
from redlock import Redlock
from passlib.context import CryptContext

# Tạo engine để kết nối với cơ sở dữ liệu
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Cấu hình Redis client
redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB,
                           decode_responses=True)

# Cấu hình Redlock client
redlock = Redlock([{"host": settings.REDIS_HOST, "port": settings.REDIS_PORT, "db": settings.REDIS_DB}])

router = APIRouter()


# Định nghĩa các mô hình dữ liệu cho FastAPI
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    taikhoan: str | None = None
    quyen: int | None = None


class UserInDB(BaseModel):
    taikhoan: str
    quyen: int
    id_gv: int | None = None
    id_hs: int | None = None


# Định nghĩa OAuth2PasswordBearer để trích xuất token từ header
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# Dependency để cung cấp kết nối với cơ sở dữ liệu
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Hàm kiểm tra mật khẩu
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# Hàm băm mật khẩu
def get_password_hash(password):
    return pwd_context.hash(password)


# Hàm lấy người dùng từ cơ sở dữ liệu
def get_user(db: Session, taikhoan: str):
    return db.query(TaiKhoan).filter(TaiKhoan.taikhoan == taikhoan).first()


# Hàm xác thực người dùng
def authenticate_user(db: Session, taikhoan: str, password: str):
    user = get_user(db, taikhoan)
    if not user or not verify_password(password, user.matkhau):
        return False
    return user


# Hàm tạo token truy cập
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


# Dependency để lấy thông tin người dùng hiện tại từ token
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        taikhoan: str = payload.get("sub")
        if taikhoan is None:
            raise credentials_exception
        token_data = TokenData(taikhoan=taikhoan, quyen=payload.get("quyen"))
    except JWTError:
        raise credentials_exception
    user = get_user(db, taikhoan=token_data.taikhoan)
    if user is None:
        raise credentials_exception
    return user


@router.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    lock = redlock.lock(f"login_lock_{form_data.username}", 1000)
    if not lock:
        raise HTTPException(status_code=429, detail="Yêu cầu quá nhiều lần! Vui lòng thử lại sau.")

    try:
        user = authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Sai tài khoản hoặc mật khẩu",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.taikhoan, "quyen": user.quyen},
            expires_delta=access_token_expires
        )
        redis_client.setex(user.taikhoan, int(access_token_expires.total_seconds()), access_token)
        return {"access_token": access_token, "token_type": "bearer"}
    finally:
        redlock.unlock(lock)


@router.post("/logout")
async def logout(current_user: TaiKhoan = Depends(get_current_user)):
    redis_client.delete(current_user.taikhoan)
    return {"message": "Đăng xuất thành công"}


# Endpoint chỉ dành cho admin
@router.get("/admin")
async def admin_only(current_user: TaiKhoan = Depends(get_current_user)):
    if current_user.quyen != 0:
        raise HTTPException(status_code=403, detail="Access forbidden")
    return {"message": "Chào mừng, Admin!"}


# Endpoint chỉ dành cho giáo viên
@router.get("/giaovien")
async def giaovien_only(current_user: TaiKhoan = Depends(get_current_user)):
    if current_user.quyen != 1:  # Chỉ cho phép giáo viên (quyen 1)
        raise HTTPException(status_code=403, detail="Access forbidden")
    return {"message": "Chào mừng, Giáo viên!"}


# Endpoint chỉ dành cho user (người dùng thông thường)
@router.get("/user")
async def user_only(current_user: TaiKhoan = Depends(get_current_user)):
    if current_user.quyen != 2:  # Chỉ cho phép người dùng thông thường (quyen 2)
        raise HTTPException(status_code=403, detail="Access forbidden")
    return {"message": "Chào mừng, User!"}
