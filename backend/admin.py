from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List
from backend import models, schemas
from backend.config import settings
from backend import crud

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


# Các route API giáo viên
@router.get("/teachers", response_model=List[schemas.GiaoVienBase])
def get_all_teachers(db: Session = Depends(get_db)):
    return crud.get_all_teachers(db)


@router.get("/teachers/{teacher_id}", response_model=schemas.GiaoVienBase)
def get_teacher_by_id(teacher_id: int, db: Session = Depends(get_db)):
    return crud.get_teacher_by_id(db, teacher_id)


@router.post("/teachers", response_model=schemas.GiaoVienResponse)
def create_teacher(teacher: schemas.GiaoVienCreate, db: Session = Depends(get_db)):
    try:
        new_teacher = crud.create_teacher(db, teacher)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Lỗi khi tạo giáo viên: {str(e)}")

    return new_teacher


@router.put("/teachers/{teacher_id}", response_model=schemas.GiaoVienBase)
def update_teacher(teacher_id: int, teacher: schemas.GiaoVienUpdate, db: Session = Depends(get_db)):
    # Gọi hàm update_teacher từ crud để cập nhật thông tin giáo viên
    db_teacher = crud.update_teacher(db, teacher_id, teacher)

    return db_teacher


@router.delete("/teachers/{teacher_id}", response_model=dict)
def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
    try:
        crud.delete_teacher(db, teacher_id)
        return {"message": "Xóa giáo viên thành công"}
    except HTTPException as e:
        raise e  # Nếu có lỗi xảy ra, ném lại lỗi để FastAPI xử lý


# Các route API học sinh
@router.get("/students", response_model=List[schemas.HocSinhResponse])
def get_all_students(db: Session = Depends(get_db)):
    students = crud.get_all_students(db)
    if not students:
        raise HTTPException(status_code=404, detail="Không có học sinh nào")
    return students


@router.get("/students/{student_id}", response_model=schemas.HocSinhResponse)
async def read_student(student_id: int, db: Session = Depends(get_db)):
    db_student = crud.get_student_by_id(db, student_id)
    return db_student


@router.post("/students", response_model=schemas.HocSinhResponse)
def create_student(student: schemas.HocSinhCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_student_with_parents(db, student)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.put("/students/{student_id}", response_model=schemas.HocSinhResponse)
def update_student(student_id: int, student: schemas.HocSinhUpdate, db: Session = Depends(get_db)):
    db_student = crud.update_student_with_parents(db, student_id, student)

    if db_student is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy học sinh")
    return db_student


@router.delete("/students/{student_id}", response_model=dict)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    # Gọi hàm delete_student trong crud
    crud.delete_student(db, student_id)
    return {"detail": "Xóa học sinh thành công"}


# Các route API lớp học
@router.get("/classes", response_model=List[schemas.LopHocBase])
def get_all_classes(db: Session = Depends(get_db)):
    classes = crud.get_all_classes(db)
    if not classes:
        raise HTTPException(status_code=404, detail="Không có lớp học nào")
    return classes


@router.get("/classes/{class_id}", response_model=schemas.LopHocResponse)
def get_class_by_id(class_id: int, db: Session = Depends(get_db)):
    cls = crud.get_class_by_id(db, class_id)
    if not cls:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học")

    return cls  # Trả về thông tin lớp học đã lấy từ CRUD


@router.post("/classes/", response_model=schemas.LopHocResponse)
def create_class_endpoint(class_data: schemas.LopHocCreate, db: Session = Depends(get_db)):
    new_class = crud.create_class(db=db, class_=class_data)
    return new_class


@router.put("/classes/{class_id}", response_model=schemas.LopHocResponse)
def update_class_endpoint(class_id: int, class_data: schemas.LopHocUpdate, db: Session = Depends(get_db)):
    return crud.update_class(db, class_id, class_data)


@router.delete("/classes/{class_id}", response_model=dict)
def delete_class(class_id: int, db: Session = Depends(get_db)):
    crud.delete_class(db, class_id)
    return {"detail": "Xóa lớp học thành công"}


# Các route API năm học
@router.get("/years", response_model=List[schemas.NamHocResponse])
def get_all_academic_years(db: Session = Depends(get_db)):
    academic_years = crud.get_academic_years(db)
    return [schemas.NamHocResponse.from_orm(year) for year in academic_years]


@router.get("/years/{year_id}", response_model=schemas.NamHocBase)
def read_academic_year_by_id(year_id: int, db: Session = Depends(get_db)):
    return crud.get_academic_year_by_id(db, year_id)


@router.post("/years/", response_model=schemas.NamHocBase)
def create_academic_year(year: schemas.NamHocCreate, db: Session = Depends(get_db)):
    return crud.create_academic_year(db, year)


@router.put("/years/{year_id}", response_model=schemas.NamHocBase)
def update_academic_year(year_id: int, year_data: schemas.NamHocUpdate, db: Session = Depends(get_db)):
    return crud.update_academic_year(db, year_id, year_data)


@router.delete("/years/{year_id}")
def delete_academic_year(year_id: int, db: Session = Depends(get_db)):
    return crud.delete_academic_year(db, year_id)

# # Các route API phụ huynh
# @router.get("/parents", response_model=List[PhuHuynhResponse])
# def get_all_parents(db: Session = Depends(get_db)):
#     parents = crud.get_all_parents(db)
#     return [PhuHuynhResponse.from_orm(parent) for parent in parents]
#
#
# @router.get("/parents/{parent_id}", response_model=PhuHuynhResponse)
# def get_parent_by_id(parent_id: int, db: Session = Depends(get_db)):
#     parent = crud.get_parent_by_id(db, parent_id)
#     if not parent:
#         raise HTTPException(status_code=404, detail="Không tìm thấy phụ huynh")
#     return PhuHuynhResponse.from_orm(parent)
#
#
# @router.post("/parents", response_model=PhuHuynhResponse)
# def create_parent(parent_data: PhuHuynhCreate, db: Session = Depends(get_db)):
#     return PhuHuynhResponse.from_orm(crud.create_parent(db, parent_data))
#
#
# @router.put("/parents/{parent_id}", response_model=PhuHuynhResponse)
# def update_parent(parent_id: int, parent_data: PhuHuynhUpdate, db: Session = Depends(get_db)):
#     db_parent = crud.update_parent(db, parent_id, parent_data)
#     if db_parent is None:
#         raise HTTPException(status_code=404, detail="Không tìm thấy phụ huynh")
#     return PhuHuynhResponse.from_orm(db_parent)
#
#
# @router.delete("/parents/{parent_id}", response_model=dict)
# def delete_parent(parent_id: int, db: Session = Depends(get_db)):
#     crud.delete_parent(db, parent_id)
#     return {"detail": "Xóa phụ huynh thành công"}
#
#
# # Các route API tài khoản
# @router.get("/accounts", response_model=List[TaiKhoanResponse])
# def get_all_accounts(db: Session = Depends(get_db)):
#     accounts = crud.get_all_accounts(db)
#     return [TaiKhoanResponse.from_orm(account) for account in accounts]
#
#
# @router.get("/accounts/{account_id}", response_model=TaiKhoanResponse)
# def get_account_by_id(account_id: int, db: Session = Depends(get_db)):
#     account = crud.get_account_by_id(db, account_id)
#     if not account:
#         raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản")
#     return TaiKhoanResponse.from_orm(account)
#
#
# @router.post("/accounts", response_model=TaiKhoanResponse)
# def create_account(account_data: TaiKhoanCreate, db: Session = Depends(get_db)):
#     return TaiKhoanResponse.from_orm(crud.create_account(db, account_data))
#
#
# @router.put("/accounts/{account_id}", response_model=TaiKhoanResponse)
# def update_account(account_id: int, account_data: TaiKhoanUpdate, db: Session = Depends(get_db)):
#     db_account = crud.update_account(db, account_id, account_data)
#     if db_account is None:
#         raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản")
#     return TaiKhoanResponse.from_orm(db_account)
#
#
# @router.delete("/accounts/{account_id}", response_model=dict)
# def delete_account(account_id: int, db: Session = Depends(get_db)):
#     crud.delete_account(db, account_id)
#     return {"detail": "Xóa tài khoản thành công"}
