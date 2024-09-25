from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.models import TaiKhoan
from backend.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import redis
from redlock import Redlock
from passlib.context import CryptContext
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cấu hình cơ sở dữ liệu
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Cấu hình Redis
redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB,
                           decode_responses=True)

# Cấu hình Redlock
redlock = Redlock([{"host": settings.REDIS_HOST, "port": settings.REDIS_PORT, "db": settings.REDIS_DB}])

router = APIRouter()


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


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db: Session, taikhoan: str):
    user = db.query(TaiKhoan).filter(TaiKhoan.taikhoan == taikhoan).first()
    logger.info(f"Đã truy xuất người dùng từ cơ sở dữ liệu: {user}")
    return user


def authenticate_user(db: Session, taikhoan: str, password: str):
    user = get_user(db, taikhoan)
    if not user or not verify_password(password, user.matkhau):
        logger.warning(f"Đăng nhập thất bại cho người dùng: {taikhoan}")
        return False
    logger.info(f"Xác thực thành công cho người dùng: {taikhoan}")
    logger.info(f"Quyền của người dùng {taikhoan}: {user.quyen}")
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    logger.info(f"Đã tạo token truy cập cho người dùng: {data.get('sub')}")
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực thông tin đăng nhập",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        logger.info(f"Đang cố gắng giải mã token: {token}")
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        logger.info(f"Payload giải mã: {payload}")

        taikhoan: str = payload.get("sub")
        if taikhoan is None:
            logger.warning("Không tìm thấy tên đăng nhập trong payload của token")
            raise credentials_exception

        stored_token = redis_client.get(taikhoan)
        logger.info(f"Token đã lưu cho {taikhoan}: {stored_token}")
        logger.info(f"Token nhận được: {token}")

        if stored_token != token:
            logger.warning(f"Token không khớp cho người dùng {taikhoan}")
            raise credentials_exception

        token_data = TokenData(taikhoan=taikhoan, quyen=payload.get("quyen"))
        logger.info(f"Đã tạo TokenData: {token_data}")
        logger.info(f"Quyền trong token: {payload.get('quyen')}")
    except JWTError as e:
        logger.error(f"Lỗi giải mã JWT: {str(e)}")
        raise credentials_exception

    user = get_user(db, taikhoan=token_data.taikhoan)
    if user is None:
        logger.warning(f"Không tìm thấy người dùng trong cơ sở dữ liệu: {token_data.taikhoan}")
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
async def logout(current_user: UserInDB = Depends(get_current_user)):
    redis_client.delete(current_user.taikhoan)
    logger.info(f"Người dùng đã đăng xuất: {current_user.taikhoan}")
    return {"message": "Đăng xuất thành công"}


@router.get("/admin")
async def admin_only(current_user: UserInDB = Depends(get_current_user)):
    logger.info(f"Yêu cầu truy cập admin từ người dùng: {current_user.taikhoan}")
    logger.info(f"Quyền của người dùng: {current_user.quyen}")
    if current_user.quyen != 0:
        logger.warning(f"Từ chối truy cập: Người dùng {current_user.taikhoan} không có quyền admin")
        raise HTTPException(status_code=403, detail="Không có quyền truy cập")
    logger.info(f"Cấp quyền truy cập admin cho người dùng: {current_user.taikhoan}")
    return {"message": "Chào mừng, Admin!"}


@router.get("/giaovien")
async def giaovien_only(current_user: UserInDB = Depends(get_current_user)):
    logger.info(f"Yêu cầu truy cập giáo viên từ người dùng: {current_user.taikhoan}")
    logger.info(f"Quyền của người dùng: {current_user.quyen}")
    if current_user.quyen != 1:
        logger.warning(f"Từ chối truy cập: Người dùng {current_user.taikhoan} không có quyền giáo viên")
        raise HTTPException(status_code=403, detail="Không có quyền truy cập")
    logger.info(f"Cấp quyền truy cập giáo viên cho người dùng: {current_user.taikhoan}")
    return {"message": "Chào mừng, Giáo viên!"}


@router.get("/user")
async def user_only(current_user: UserInDB = Depends(get_current_user)):
    logger.info(f"Yêu cầu truy cập người dùng từ: {current_user.taikhoan}")
    logger.info(f"Quyền của người dùng: {current_user.quyen}")
    if current_user.quyen != 2:
        logger.warning(f"Từ chối truy cập: {current_user.taikhoan} không có quyền người dùng thông thường")
        raise HTTPException(status_code=403, detail="Không có quyền truy cập")
    logger.info(f"Cấp quyền truy cập người dùng cho: {current_user.taikhoan}")
    return {"message": "Chào mừng, Người dùng!"}


@router.get("/admin/me", response_model=UserInDB)
async def read_users_me(current_user: UserInDB = Depends(get_current_user)):
    logger.info(f"Yêu cầu thông tin người dùng: {current_user.taikhoan}")
    return current_user