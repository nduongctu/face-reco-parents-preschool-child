from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import GiaoVien as GiaoVienModel, LopHoc as LopHocModel, LopHoc_GiaoVien as LopHocGiaoVienModel
from config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from typing import Optional, List
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


class LopHocBase(BaseModel):
    lophoc: str

    @classmethod
    def from_orm(cls, obj):
        return cls(lophoc=obj.lophoc)


class GiaoVienBase(BaseModel):
    id_gv: int
    ten_gv: str
    gioitinh_gv: str
    ngaysinh_gv: date
    diachi_gv: str
    sdt_gv: str
    lop_hoc: Optional[List[LopHocBase]] = []

    @classmethod
    def from_orm(cls, obj):
        lop_hoc_list = [LopHocBase.from_orm(lop) for lop in obj.lop_hoc] if obj.lop_hoc else []
        return cls(
            id_gv=obj.id_gv,
            ten_gv=obj.ten_gv,
            gioitinh_gv=obj.gioitinh_gv,
            ngaysinh_gv=obj.ngaysinh_gv,
            diachi_gv=obj.diachi_gv,
            sdt_gv=obj.sdt_gv,
            lop_hoc=lop_hoc_list
        )


class GiaoVienUpdate(BaseModel):
    ten_gv: Optional[str] = None
    gioitinh_gv: Optional[str] = None
    ngaysinh_gv: Optional[date] = None
    diachi_gv: Optional[str] = None
    sdt_gv: Optional[str] = None


class GiaoVienCreate(BaseModel):
    ten_gv: str
    gioitinh_gv: str
    ngaysinh_gv: date
    diachi_gv: str
    sdt_gv: str


@router.get("/teachers", response_model=List[GiaoVienBase])
def get_all_teachers(db: Session = Depends(get_db)):
    # Lấy danh sách tất cả giáo viên
    teachers = db.query(GiaoVienModel).all()

    if not teachers:
        raise HTTPException(status_code=404, detail="Không có giáo viên nào")

    # Tạo danh sách giáo viên với thông tin lớp học
    teachers_response = []
    for teacher in teachers:
        # Lấy danh sách các lớp mà giáo viên dạy
        lop_hoc = db.query(LopHocModel).join(LopHocGiaoVienModel).filter(
            LopHocGiaoVienModel.id_gv == teacher.id_gv).all()

        # Tạo đối tượng GiaoVienBase với lớp học
        teacher_response = GiaoVienBase.from_orm(teacher)
        teacher_response.lop_hoc = [LopHocBase.from_orm(lop) for lop in lop_hoc]

        teachers_response.append(teacher_response)

    return teachers_response


@router.get("/teachers/{teacher_id}", response_model=GiaoVienBase)
def get_teacher_by_id(teacher_id: int, db: Session = Depends(get_db)):
    # Lấy thông tin giáo viên theo ID
    teacher = db.query(GiaoVienModel).filter(GiaoVienModel.id_gv == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Không tìm thấy giáo viên")

    # Lấy danh sách các lớp mà giáo viên dạy
    lop_hoc = db.query(LopHocModel).join(LopHocGiaoVienModel).filter(
        LopHocGiaoVienModel.id_gv == teacher_id).all()

    # Tạo đối tượng GiaoVienBase với lớp học
    teacher_response = GiaoVienBase.from_orm(teacher)
    teacher_response.lop_hoc = [LopHocBase.from_orm(lop) for lop in lop_hoc]

    return teacher_response


@router.put("/teachers/{teacher_id}", response_model=GiaoVienBase)
def update_teacher_info(teacher_id: int, teacher_data: GiaoVienUpdate, db: Session = Depends(get_db)):
    # Lấy thông tin giáo viên từ cơ sở dữ liệu
    teacher = db.query(GiaoVienModel).filter(GiaoVienModel.id_gv == teacher_id).first()
    if teacher is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy giáo viên")

    # Cập nhật thông tin giáo viên
    if teacher_data.ten_gv is not None:
        teacher.ten_gv = teacher_data.ten_gv
    if teacher_data.gioitinh_gv is not None:
        teacher.gioitinh_gv = teacher_data.gioitinh_gv
    if teacher_data.ngaysinh_gv is not None:
        teacher.ngaysinh_gv = teacher_data.ngaysinh_gv
    if teacher_data.diachi_gv is not None:
        teacher.diachi_gv = teacher_data.diachi_gv
    if teacher_data.sdt_gv is not None:
        teacher.sdt_gv = teacher_data.sdt_gv

    # Lưu thay đổi vào cơ sở dữ liệu
    db.commit()

    # Đọc lại thông tin giáo viên đã cập nhật để trả về
    updated_teacher = db.query(GiaoVienModel).filter(GiaoVienModel.id_gv == teacher_id).first()
    return GiaoVienBase.from_orm(updated_teacher)


@router.delete("/teachers/{teacher_id}")
def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
    teacher = db.query(GiaoVienModel).filter(GiaoVienModel.id_gv == teacher_id).first()
    if teacher is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy giáo viên")

    db.delete(teacher)
    db.commit()

    return {"detail": "Xóa giáo viên thành công"}


@router.post("/teachers", response_model=GiaoVienBase)
def create_teacher(teacher_data: GiaoVienCreate, db: Session = Depends(get_db)):
    # Kiểm tra xem số điện thoại đã tồn tại hay chưa
    existing_teacher = db.query(GiaoVienModel).filter(GiaoVienModel.sdt_gv == teacher_data.sdt_gv).first()
    if existing_teacher:
        raise HTTPException(status_code=400, detail="Số điện thoại đã được sử dụng")

    # Tạo mới đối tượng giáo viên
    new_teacher = GiaoVienModel(
        ten_gv=teacher_data.ten_gv,
        gioitinh_gv=teacher_data.gioitinh_gv,
        ngaysinh_gv=teacher_data.ngaysinh_gv,
        diachi_gv=teacher_data.diachi_gv,
        sdt_gv=teacher_data.sdt_gv
    )

    # Thêm giáo viên vào cơ sở dữ liệu và commit
    db.add(new_teacher)
    db.commit()
    db.refresh(new_teacher)  # Làm mới đối tượng để nhận được giá trị mới nhất, bao gồm id

    # Trả về thông tin giáo viên đã thêm
    return GiaoVienBase.from_orm(new_teacher)
