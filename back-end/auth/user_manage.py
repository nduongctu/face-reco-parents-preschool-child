from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import redis
from redlock import Redlock
from pydantic import BaseModel
from config import settings

# Tạo engine để kết nối với cơ sở dữ liệu
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Cấu hình Redis client
redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)

# Cấu hình Redlock client
redlock = Redlock([{"host": settings.REDIS_HOST, "port": settings.REDIS_PORT, "db": settings.REDIS_DB}])


# Định nghĩa mô hình User cho cơ sở dữ liệu
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(100))
    role = Column(Integer, default=1)


# Tạo bảng trong cơ sở dữ liệu
Base.metadata.create_all(bind=engine)


# Định nghĩa các mô hình dữ liệu cho FastAPI
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    role: int | None = None


class UserInDB(BaseModel):
    username: str
    role: int


# Tạo đối tượng FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


# Hàm xác thực người dùng
def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
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
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username, role=payload.get("role"))
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


# Endpoint đăng ký người dùng mới
@app.post("/register", response_model=Token)
def register(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    lock = redlock.lock("register_lock", 1000)
    if not lock:
        raise HTTPException(status_code=429, detail="Yêu cầu quá nhiều lần! Vui lòng thử lại sau.")

    try:
        existing_user = get_user(db, form_data.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username đã tồn tại")

        hashed_password = get_password_hash(form_data.password)
        new_user = User(
            username=form_data.username,
            hashed_password=hashed_password
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": new_user.username, "role": new_user.role},
            expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    finally:
        redlock.unlock(lock)


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
                detail="Sai username hoặc password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "role": user.role},
            expires_delta=access_token_expires
        )
        redis_client.setex(user.username, int(access_token_expires.total_seconds()), access_token)
        return {"access_token": access_token, "token_type": "bearer"}
    finally:
        redlock.unlock(lock)


# Endpoint lấy thông tin người dùng hiện tại
@app.get("/users/me", response_model=UserInDB)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return UserInDB(username=current_user.username, role=current_user.role)


# Endpoint chỉ dành cho admin
@app.get("/admin")
async def admin_only(current_user: User = Depends(get_current_user)):
    if current_user.role != 0:
        raise HTTPException(status_code=403, detail="Access forbidden")
    return {"message": "Chào mừng, Admin!"}


# Chạy ứng dụng FastAPI
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)