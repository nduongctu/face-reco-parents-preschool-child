from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from typing import Optional, List, ForwardRef
from datetime import date

# Import các mô hình từ models
from models import (
    GiaoVien as GiaoVienModel,
    LopHoc as LopHocModel,
    LopHoc_GiaoVien as LopHocGiaoVienModel,
    HocSinh as HocSinhModel,
    LopHoc_HocSinh as LopHocHocSinhModel,
    NamHoc as NamHocModel
)
from config import settings

# Tạo engine và session để kết nối với cơ sở dữ liệu
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Các lớp Pydantic
GiaoVienBase = ForwardRef('GiaoVienBase')
LopHocBase = ForwardRef('LopHocBase')


class LopHocBase(BaseModel):
    id_lh: int
    lophoc: str
    id_nh: Optional[int] = None  # Thêm trường này
    giao_vien: Optional[List[GiaoVienBase]] = []

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id_lh=obj.id_lh,
            lophoc=obj.lophoc,
            id_nh=obj.id_nh,
            giao_vien=[GiaoVienBase.from_orm(gv.giao_vien) for gv in obj.giao_vien_lop] if obj.giao_vien_lop else []
        )


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


class NamHocBase(BaseModel):
    id_nh: int
    namhoc: str

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id_nh=obj.id_nh,
            namhoc=obj.namhoc
        )


GiaoVienBase.update_forward_refs()
LopHocBase.update_forward_refs()


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


class HocSinhBase(BaseModel):
    id_hs: int
    ten_hs: str
    gioitinh_hs: str
    ngaysinh_hs: date
    lop_hoc: Optional[List[LopHocBase]] = []

    @classmethod
    def from_orm(cls, obj):
        lop_hoc_list = [LopHocBase.from_orm(lop) for lop in obj.lop_hoc_hs] if obj.lop_hoc_hs else []
        return cls(
            id_hs=obj.id_hs,
            ten_hs=obj.ten_hs,
            gioitinh_hs=obj.gioitinh_hs,
            ngaysinh_hs=obj.ngaysinh_hs,
            lop_hoc=lop_hoc_list
        )


class HocSinhCreate(BaseModel):
    ten_hs: str
    gioitinh_hs: str
    ngaysinh_hs: date
    lop_hoc_ids: Optional[List[int]] = []


class HocSinhUpdate(BaseModel):
    ten_hs: Optional[str] = None
    gioitinh_hs: Optional[str] = None
    ngaysinh_hs: Optional[date] = None
    lop_hoc_ids: Optional[List[int]] = []


class LopHocCreate(BaseModel):
    lophoc: str
    id_nh: int
    giao_vien_ids: Optional[List[int]] = None  # Nếu cần quản lý nhiều giáo viên


class LopHocUpdate(BaseModel):
    lophoc: Optional[str] = None


# Các route API

@router.get("/teachers", response_model=List[GiaoVienBase])
def get_all_teachers(db: Session = Depends(get_db)):
    teachers = db.query(GiaoVienModel).all()
    if not teachers:
        raise HTTPException(status_code=404, detail="Không có giáo viên nào")

    teachers_response = []
    for teacher in teachers:
        lop_hoc = db.query(LopHocModel).join(LopHocGiaoVienModel).filter(
            LopHocGiaoVienModel.id_gv == teacher.id_gv).all()
        teacher_response = GiaoVienBase.from_orm(teacher)
        teacher_response.lop_hoc = [LopHocBase.from_orm(lop) for lop in lop_hoc]
        teachers_response.append(teacher_response)

    return teachers_response


@router.get("/teachers/{teacher_id}", response_model=GiaoVienBase)
def get_teacher_by_id(teacher_id: int, db: Session = Depends(get_db)):
    teacher = db.query(GiaoVienModel).filter(GiaoVienModel.id_gv == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Không tìm thấy giáo viên")

    lop_hoc = db.query(LopHocModel).join(LopHocGiaoVienModel).filter(
        LopHocGiaoVienModel.id_gv == teacher_id).all()
    teacher_response = GiaoVienBase.from_orm(teacher)
    teacher_response.lop_hoc = [LopHocBase.from_orm(lop) for lop in lop_hoc]

    return teacher_response


@router.put("/teachers/{teacher_id}", response_model=GiaoVienBase)
def update_teacher_info(teacher_id: int, teacher_data: GiaoVienUpdate, db: Session = Depends(get_db)):
    teacher = db.query(GiaoVienModel).filter(GiaoVienModel.id_gv == teacher_id).first()
    if teacher is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy giáo viên")

    for attr, value in teacher_data.dict(exclude_unset=True).items():
        setattr(teacher, attr, value)

    db.commit()
    updated_teacher = db.query(GiaoVienModel).filter(GiaoVienModel.id_gv == teacher_id).first()
    return GiaoVienBase.from_orm(updated_teacher)


@router.delete("/teachers/{teacher_id}")
def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
    teacher = db.query(GiaoVienModel).filter(GiaoVienModel.id_gv == teacher_id).first()
    if teacher is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy giáo viên")

    db.query(LopHocGiaoVienModel).filter(LopHocGiaoVienModel.id_gv == teacher_id).delete()
    db.delete(teacher)
    db.commit()

    return {"detail": "Xóa giáo viên thành công"}


@router.post("/teachers", response_model=GiaoVienBase)
def create_teacher(teacher_data: GiaoVienCreate, db: Session = Depends(get_db)):
    existing_teacher = db.query(GiaoVienModel).filter(GiaoVienModel.sdt_gv == teacher_data.sdt_gv).first()
    if existing_teacher:
        raise HTTPException(status_code=400, detail="Số điện thoại đã được sử dụng")

    new_teacher = GiaoVienModel(**teacher_data.dict())
    db.add(new_teacher)
    db.commit()
    db.refresh(new_teacher)

    return GiaoVienBase.from_orm(new_teacher)


@router.get("/students", response_model=List[HocSinhBase])
def get_all_students(db: Session = Depends(get_db)):
    students = db.query(HocSinhModel).all()
    if not students:
        raise HTTPException(status_code=404, detail="Không có học sinh nào")

    students_response = []
    for student in students:
        lop_hoc = db.query(LopHocModel).join(LopHocHocSinhModel).filter(
            LopHocHocSinhModel.id_hs == student.id_hs).all()
        student_response = HocSinhBase.from_orm(student)
        student_response.lop_hoc = [LopHocBase.from_orm(lop) for lop in lop_hoc]
        students_response.append(student_response)

    return students_response


@router.get("/students/{student_id}", response_model=HocSinhBase)
def get_student_by_id(student_id: int, db: Session = Depends(get_db)):
    student = db.query(HocSinhModel).filter(HocSinhModel.id_hs == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Không tìm thấy học sinh")

    lop_hoc = db.query(LopHocModel).join(LopHocHocSinhModel).filter(
        LopHocHocSinhModel.id_hs == student_id).all()
    student_response = HocSinhBase.from_orm(student)
    student_response.lop_hoc = [LopHocBase.from_orm(lop) for lop in lop_hoc]

    return student_response


@router.post("/students", response_model=HocSinhBase)
def create_student(student_data: HocSinhCreate, db: Session = Depends(get_db)):
    new_student = HocSinhModel(**student_data.dict(exclude={"lop_hoc_ids"}))
    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    if student_data.lop_hoc_ids:
        for lop_id in student_data.lop_hoc_ids:
            lop_hoc_hs = LopHocHocSinhModel(id_hs=new_student.id_hs, id_lh=lop_id)
            db.add(lop_hoc_hs)
        db.commit()

    return HocSinhBase.from_orm(new_student)


@router.put("/students/{student_id}", response_model=HocSinhBase)
def update_student_info(student_id: int, student_data: HocSinhUpdate, db: Session = Depends(get_db)):
    student = db.query(HocSinhModel).filter(HocSinhModel.id_hs == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy học sinh")

    for attr, value in student_data.dict(exclude_unset=True).items():
        setattr(student, attr, value)

    db.commit()

    if student_data.lop_hoc_ids:
        db.query(LopHocHocSinhModel).filter(LopHocHocSinhModel.id_hs == student_id).delete()
        for lop_id in student_data.lop_hoc_ids:
            lop_hoc_hs = LopHocHocSinhModel(id_hs=student.id_hs, id_lh=lop_id)
            db.add(lop_hoc_hs)
        db.commit()

    return HocSinhBase.from_orm(student)


@router.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(HocSinhModel).filter(HocSinhModel.id_hs == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy học sinh")

    db.query(LopHocHocSinhModel).filter(LopHocHocSinhModel.id_hs == student_id).delete()
    db.delete(student)
    db.commit()

    return {"detail": "Xóa học sinh thành công"}


@router.get("/classes", response_model=List[LopHocBase])
def get_all_classes(db: Session = Depends(get_db)):
    classes = db.query(LopHocModel).all()
    if not classes:
        raise HTTPException(status_code=404, detail="Không có lớp học nào")

    classes_response = []
    for cls in classes:
        giao_vien = db.query(GiaoVienModel).join(LopHocGiaoVienModel).filter(
            LopHocGiaoVienModel.id_lh == cls.id_lh).all()
        cls_response = LopHocBase.from_orm(cls)
        cls_response.giao_vien = [GiaoVienBase.from_orm(gv) for gv in giao_vien]
        classes_response.append(cls_response)

    return classes_response


@router.get("/classes/{class_id}", response_model=LopHocBase)
def get_class_by_id(class_id: int, db: Session = Depends(get_db)):
    cls = db.query(LopHocModel).filter(LopHocModel.id_lh == class_id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học")

    giao_vien = db.query(GiaoVienModel).join(LopHocGiaoVienModel).filter(
        LopHocGiaoVienModel.id_lh == class_id).all()
    cls_response = LopHocBase.from_orm(cls)
    cls_response.giao_vien = [GiaoVienBase.from_orm(gv) for gv in giao_vien]

    return cls_response


@router.post("/classes", response_model=LopHocBase)
def create_class(class_data: LopHocCreate, db: Session = Depends(get_db)):
    existing_class = db.query(LopHocModel).filter(LopHocModel.lophoc == class_data.lophoc).first()
    if existing_class:
        raise HTTPException(status_code=400, detail="Lớp học đã tồn tại")

    # Tạo đối tượng lớp học mới
    new_class = LopHocModel(
        lophoc=class_data.lophoc,
        id_nh=class_data.id_nh
    )
    db.add(new_class)
    db.commit()
    db.refresh(new_class)

    # Thêm giáo viên nếu có
    if class_data.giao_vien_ids:
        for gv_id in class_data.giao_vien_ids:
            lop_hoc_gv = LopHoc_GiaoVien(id_lh=new_class.id_lh, id_gv=gv_id)
            db.add(lop_hoc_gv)
        db.commit()

    return LopHocBase.from_orm(new_class)


@router.delete("/classes/{class_id}")
def delete_class(class_id: int, db: Session = Depends(get_db)):
    cls = db.query(LopHocModel).filter(LopHocModel.id_lh == class_id).first()
    if cls is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học")

    db.query(LopHocGiaoVienModel).filter(LopHocGiaoVienModel.id_lh == class_id).delete()
    db.query(LopHocHocSinhModel).filter(LopHocHocSinhModel.id_lh == class_id).delete()
    db.delete(cls)
    db.commit()

    return {"detail": "Xóa lớp học thành công"}


@router.get("/years", response_model=List[NamHocBase])
def get_academic_years(db: Session = Depends(get_db)):
    academic_years = db.query(NamHocModel).all()
    if not academic_years:
        raise HTTPException(status_code=404, detail="Không tìm thấy năm học nào")
    return [NamHocBase.from_orm(year) for year in academic_years]
