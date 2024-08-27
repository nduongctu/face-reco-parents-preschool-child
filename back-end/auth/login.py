from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import sessionmaker, Session, declarative_base, relationship
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import redis
from redlock import Redlock
from pydantic import BaseModel
from config import settings
from middleware import TokenExpiryMiddleware

# Tạo engine để kết nối với cơ sở dữ liệu
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Cấu hình Redis client
redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB,
                           decode_responses=True)

# Cấu hình Redlock client
redlock = Redlock([{"host": settings.REDIS_HOST, "port": settings.REDIS_PORT, "db": settings.REDIS_DB}])


# Định nghĩa mô hình TaiKhoan cho cơ sở dữ liệu
class TaiKhoan(Base):
    __tablename__ = "TaiKhoan"
    id_taikhoan = Column(Integer, primary_key=True, index=True, autoincrement=True)
    taikhoan = Column(String(50), unique=True, index=True)
    matkhau = Column(String(255))
    quyen = Column(Integer)
    id_gv = Column(Integer, ForeignKey('GiaoVien.id_gv'), nullable=True)
    id_hs = Column(Integer, ForeignKey('HocSinh.id_hs'), nullable=True)

    # Relationships
    giao_vien = relationship("GiaoVien", back_populates="tai_khoan", uselist=False)
    hoc_sinh = relationship("HocSinh", back_populates="tai_khoan", uselist=False)


class GiaoVien(Base):
    __tablename__ = "GiaoVien"
    id_gv = Column(Integer, primary_key=True, index=True)
    ten_gv = Column(String(100), nullable=False)
    gioitinh_gv = Column(String(5), nullable=False)
    ngaysinh_gv = Column(Date, nullable=False)
    diachi_gv = Column(String(200), nullable=False)
    sdt_gv = Column(String(20), nullable=False)

    # Relationships
    tai_khoan = relationship("TaiKhoan", back_populates="giao_vien", uselist=False)


class HocSinh(Base):
    __tablename__ = "HocSinh"
    id_hs = Column(Integer, primary_key=True, index=True)
    ten_hs = Column(String(100), nullable=False)
    gioitinh_hs = Column(String(5), nullable=False)
    ngaysinh_hs = Column(Date, nullable=False)

    # Relationships
    tai_khoan = relationship("TaiKhoan", back_populates="hoc_sinh", uselist=False)


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


# Tạo đối tượng FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TokenExpiryMiddleware)  # Thêm middleware kiểm tra token hết hạn

# Đối tượng để quản lý mật khẩu
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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


# Endpoint đăng nhập và lấy token
@app.post("/token", response_model=Token)
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


# Endpoint đăng xuất
@app.post("/logout")
async def logout(current_user: TaiKhoan = Depends(get_current_user)):
    redis_client.delete(current_user.taikhoan)
    return {"message": "Đăng xuất thành công"}


# Endpoint lấy thông tin người dùng hiện tại
@app.get("/users/me", response_model=UserInDB)
async def read_users_me(current_user: TaiKhoan = Depends(get_current_user)):
    return UserInDB(
        taikhoan=current_user.taikhoan,
        quyen=current_user.quyen,
        id_gv=current_user.id_gv,
        id_hs=current_user.id_hs
    )


# Endpoint chỉ dành cho admin
@app.get("/admin")
async def admin_only(current_user: TaiKhoan = Depends(get_current_user)):
    if current_user.quyen != 0:
        raise HTTPException(status_code=403, detail="Access forbidden")
    return {"message": "Chào mừng, Admin!"}


# Endpoint chỉ dành cho giáo viên
@app.get("/giaovien")
async def giaovien_only(current_user: TaiKhoan = Depends(get_current_user)):
    if current_user.quyen != 1:  # Chỉ cho phép giáo viên (quyen 1)
        raise HTTPException(status_code=403, detail="Access forbidden")
    return {"message": "Chào mừng, Giáo viên!"}


# Endpoint chỉ dành cho user (người dùng thông thường)
@app.get("/user")
async def user_only(current_user: TaiKhoan = Depends(get_current_user)):
    if current_user.quyen != 2:  # Chỉ cho phép người dùng thông thường (quyen 2)
        raise HTTPException(status_code=403, detail="Access forbidden")
    return {"message": "Chào mừng, User!"}


# Chạy ứng dụng FastAPI
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
