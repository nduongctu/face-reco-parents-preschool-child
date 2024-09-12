from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import GiaoVien as GiaoVienModel
from config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from typing import Optional
from datetime import date

# Tạo engine để kết nối với cơ sở dữ liệu
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic model cho giáo viên
class GiaoVienBase(BaseModel):
    ten_gv: str
    gioitinh_gv: str
    ngaysinh_gv: date
    diachi_gv: str
    sdt_gv: str

    class Config:
        from_attributes = True

class GiaoVienUpdate(GiaoVienBase):
    pass

@router.get("/teachers/{teacher_id}", response_model=GiaoVienBase)
def get_teacher_info(teacher_id: int, db: Session = Depends(get_db)):
    teacher = db.query(GiaoVienModel).filter(GiaoVienModel.id_gv == teacher_id).first()
    if teacher is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy giáo viên")
    return teacher

@router.put("/teachers/{teacher_id}", response_model=dict)
def update_teacher_info(teacher_id: int, teacher_data: GiaoVienUpdate, db: Session = Depends(get_db)):
    teacher = db.query(GiaoVienModel).filter(GiaoVienModel.id_gv == teacher_id).first()
    if teacher is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy giáo viên")

    # Cập nhật thông tin giáo viên
    teacher.ten_gv = teacher_data.ten_gv
    teacher.gioitinh_gv = teacher_data.gioitinh_gv
    teacher.ngaysinh_gv = teacher_data.ngaysinh_gv
    teacher.diachi_gv = teacher_data.diachi_gv
    teacher.sdt_gv = teacher_data.sdt_gv

    db.commit()
    return {"message": "Cập nhật thông tin thành công"}
