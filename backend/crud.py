from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# Lấy tất cả giáo viên
def get_all_teachers(db: Session):
    return db.query(models.GiaoVien).all()


# Lấy giáo viên theo ID
def get_teacher_by_id(db: Session, teacher_id: int):
    teacher = db.query(models.GiaoVien).filter(models.GiaoVien.id_gv == teacher_id).first()
    if teacher is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy giáo viên")
    return teacher


# Tạo một giáo viên mới
def create_teacher(db: Session, teacher: schemas.GiaoVienCreate):
    # Create the new account
    new_account = models.TaiKhoan(
        taikhoan=teacher.taikhoan,
        matkhau=hash_password(teacher.matkhau),  # Ensure you have a function to hash passwords
        quyen=teacher.quyen
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)

    # Create the new teacher and associate it with the account
    new_teacher = models.GiaoVien(
        ten_gv=teacher.ten_gv,
        gioitinh_gv=teacher.gioitinh_gv,
        ngaysinh_gv=teacher.ngaysinh_gv,
        diachi_gv=teacher.diachi_gv,
        sdt_gv=teacher.sdt_gv,
    )
    db.add(new_teacher)
    try:
        db.commit()
        db.refresh(new_teacher)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return new_teacher


# Cập nhật một giáo viên
def update_teacher(db: Session, teacher_id: int, teacher: schemas.GiaoVienUpdate):
    db_teacher = db.query(models.GiaoVien).filter(models.GiaoVien.id_gv == teacher_id).first()
    if db_teacher is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy giáo viên")

    # Update the teacher fields
    for key, value in teacher.dict(exclude={"quyen"}).items():
        if value is not None:
            setattr(db_teacher, key, value)

    # Update the quyen field of the associated account if provided
    if teacher.quyen is not None:
        db_account = db.query(models.TaiKhoan).filter(models.TaiKhoan.id_taikhoan == db_teacher.id_taikhoan).first()
        db_account.quyen = teacher.quyen

    db.commit()
    db.refresh(db_teacher)
    return db_teacher


# Xóa một giáo viên
def delete_teacher(db: Session, teacher_id: int):
    db_teacher = db.query(models.GiaoVien).filter(models.GiaoVien.id_gv == teacher_id).first()
    if db_teacher is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy giáo viên")

    # Retrieve the associated account
    db_account = db.query(models.TaiKhoan).filter(models.TaiKhoan.id_taikhoan == db_teacher.id_taikhoan).first()
    if db_account is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản")

    # Delete the teacher and the associated account
    db.delete(db_teacher)
    db.delete(db_account)
    db.commit()


# Lấy tất cả học sinh
def get_all_students(db: Session):
    return db.query(models.HocSinh).all()


# Lấy học sinh theo ID
def get_student_by_id(db: Session, student_id: int):
    student = db.query(models.HocSinh).filter(models.HocSinh.id_hs == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy học sinh")
    return student


# Tạo một học sinh mới
def create_student(db: Session, student: schemas.HocSinhCreate):
    # Tạo tài khoản mới cho học sinh
    new_account = models.TaiKhoan(
        taikhoan=student.taikhoan,
        matkhau=hash_password(student.matkhau),
        quyen=2  # Mặc định quyền cho học sinh
    )

    db.add(new_account)
    db.commit()
    db.refresh(new_account)

    # Tạo học sinh mới và liên kết với tài khoản vừa tạo
    new_student = models.HocSinh(
        ten_hs=student.ten_hs,
        gioitinh_hs=student.gioitinh_hs,
        ngaysinh_hs=student.ngaysinh_hs,
    )

    db.add(new_student)
    try:
        db.commit()
        db.refresh(new_student)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    return new_student


# Cập nhật một học sinh
def update_student(db: Session, student_id: int, student: schemas.HocSinhUpdate):
    db_student = db.query(models.HocSinh).filter(models.HocSinh.id_hs == student_id).first()
    if db_student is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy học sinh")

    for key, value in student.dict(exclude_unset=True).items():  # Chỉ cập nhật những trường được cung cấp
        setattr(db_student, key, value)

    db.commit()
    db.refresh(db_student)
    return db_student


# Xoá một học sinh
def delete_student(db: Session, student_id: int):
    db_student = db.query(models.HocSinh).filter(models.HocSinh.id_hs == student_id).first()
    if db_student is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy học sinh")

    # Xoá tài khoản liên quan
    db_account = db.query(models.TaiKhoan).filter(models.TaiKhoan.id_taikhoan == db_student.id_taikhoan).first()
    if db_account:
        db.delete(db_account)

    # Xoá phụ huynh liên quan (nếu cần)
    db_parent = db.query(models.PhuHuynh).filter(models.PhuHuynh.id_ph == db_student.id_ph).first()
    if db_parent:
        db.delete(db_parent)

    # Xoá học sinh
    db.delete(db_student)
    db.commit()


# Lấy tất cả lớp học
def get_all_classes(db: Session):
    return db.query(models.LopHoc).all()


# Lấy lớp học theo ID
def get_class_by_id(db: Session, class_id: int):
    cls = db.query(models.LopHoc).filter(models.LopHoc.id_lh == class_id).first()
    if cls is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học")
    return cls


# Tạo một lớp học mới
def create_class(db: Session, class_: schemas.LopHocCreate):
    new_class = models.LopHoc(**class_.dict())
    db.add(new_class)
    try:
        db.commit()
        db.refresh(new_class)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return new_class


# Cập nhật một lớp học
def update_class(db: Session, class_id: int, class_: schemas.LopHocUpdate):
    db_class = db.query(models.LopHoc).filter(models.LopHoc.id_lh == class_id).first()
    if db_class is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học")

    for key, value in class_.dict().items():
        if value is not None:  # Only update if the value is provided
            setattr(db_class, key, value)

    db.commit()
    db.refresh(db_class)
    return db_class


# Xóa một lớp học
def delete_class(db: Session, class_id: int):
    db_class = db.query(models.LopHoc).filter(models.LopHoc.id_lh == class_id).first()
    if db_class is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học")

    db.delete(db_class)
    db.commit()


# Lấy tất cả năm học
def get_academic_years(db: Session):
    academic_years = db.query(models.NamHoc).all()
    if not academic_years:
        raise HTTPException(status_code=404, detail="Không tìm thấy năm học nào")
    return academic_years


# Lấy năm học theo ID
def get_academic_year_by_id(db: Session, year_id: int):
    academic_year = db.query(models.NamHoc).filter(models.NamHoc.id_nh == year_id).first()
    if not academic_year:
        raise HTTPException(status_code=404, detail="Không tìm thấy năm học")
    return academic_year


# Tạo một năm học mới
def create_academic_year(db: Session, year_data: schemas.NamHocBase):
    new_year = models.NamHoc(namhoc=year_data.namhoc)
    db.add(new_year)
    db.commit()
    db.refresh(new_year)
    return new_year


# Cập nhật một năm học
def update_academic_year(db: Session, year_id: int, year_data: schemas.NamHocBase):
    academic_year = db.query(models.NamHoc).filter(models.NamHoc.id_nh == year_id).first()
    if not academic_year:
        raise HTTPException(status_code=404, detail="Không tìm thấy năm học")
    academic_year.namhoc = year_data.namhoc
    db.commit()
    db.refresh(academic_year)
    return academic_year


# Xóa một năm học
def delete_academic_year(db: Session, year_id: int):
    academic_year = db.query(models.NamHoc).filter(models.NamHoc.id_nh == year_id).first()
    if not academic_year:
        raise HTTPException(status_code=404, detail="Không tìm thấy năm học")
    db.delete(academic_year)
    db.commit()


# Lấy tất cả phụ huynh
def get_all_parents(db: Session):
    return db.query(models.PhuHuynh).all()


# Lấy phụ huynh theo ID
def get_parent_by_id(db: Session, parent_id: int):
    parent = db.query(models.PhuHuynh).filter(models.PhuHuynh.id_ph == parent_id).first()
    if parent is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy phụ huynh")
    return parent


# Tạo một phụ huynh mới
def create_parent(db: Session, parent: schemas.PhuHuynhCreate):
    new_parent = models.PhuHuynh(**parent.dict())
    db.add(new_parent)
    try:
        db.commit()
        db.refresh(new_parent)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return new_parent


# Cập nhật một phụ huynh
def update_parent(db: Session, parent_id: int, parent: schemas.PhuHuynhUpdate):
    db_parent = db.query(models.PhuHuynh).filter(models.PhuHuynh.id_ph == parent_id).first()
    if db_parent is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy phụ huynh")
    for key, value in parent.dict().items():
        if value is not None:
            setattr(db_parent, key, value)
    db.commit()
    db.refresh(db_parent)
    return db_parent


# Xóa một phụ huynh
def delete_parent(db: Session, parent_id: int):
    db_parent = db.query(models.PhuHuynh).filter(models.PhuHuynh.id_ph == parent_id).first()
    if db_parent is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy phụ huynh")
    db.delete(db_parent)
    db.commit()


# Lấy tất cả tài khoản
def get_all_accounts(db: Session):
    return db.query(models.TaiKhoan).all()


# Lấy tài khoản theo ID
def get_account_by_id(db: Session, account_id: int):
    account = db.query(models.TaiKhoan).filter(models.TaiKhoan.id_taikhoan == account_id).first()
    if account is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản")
    return account


# Tạo một tài khoản mới
def create_account(db: Session, account: schemas.TaiKhoanCreate):
    new_account = models.TaiKhoan(**account.dict())
    db.add(new_account)
    try:
        db.commit()
        db.refresh(new_account)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return new_account


# Cập nhật một tài khoản
def update_account(db: Session, account_id: int, account: schemas.TaiKhoanUpdate):
    db_account = db.query(models.TaiKhoan).filter(models.TaiKhoan.id_taikhoan == account_id).first()
    if db_account is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản")
    for key, value in account.dict().items():
        if value is not None:
            setattr(db_account, key, value)
    db.commit()
    db.refresh(db_account)
    return db_account


# Xóa một tài khoản
def delete_account(db: Session, account_id: int):
    db_account = db.query(models.TaiKhoan).filter(models.TaiKhoan.id_taikhoan == account_id).first()
    if db_account is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản")
    db.delete(db_account)
    db.commit()
