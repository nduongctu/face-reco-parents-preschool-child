from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from backend import models, schemas
from passlib.context import CryptContext
from typing import List, Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password):
    return pwd_context.hash(password)


# =======================
# Teacher CRUD Functions
# =======================
def get_all_teachers(db: Session) -> List[schemas.GiaoVienResponse]:
    # Query bảng GiaoVien và join với TaiKhoan và LopHoc
    teachers = db.query(models.GiaoVien).options(
        joinedload(models.GiaoVien.tai_khoan),  # Load thông tin tài khoản
        joinedload(models.GiaoVien.lop_hocs)  # Load thông tin lớp học
    ).all()

    # Xử lý dữ liệu và chuyển đổi thành mô hình Pydantic
    result = []
    for teacher in teachers:
        # Lấy quyền tài khoản từ bảng TaiKhoan (nếu có)
        tai_khoan_quyen = teacher.tai_khoan.quyen if teacher.tai_khoan else None

        # Lấy danh sách tên lớp học từ bảng LopHoc (nếu có)
        lop_hoc_ten = [lop.lophoc for lop in teacher.lop_hocs] if teacher.lop_hocs else []

        # Lấy id_taikhoan từ bảng TaiKhoan (nếu có)
        id_taikhoan = teacher.tai_khoan.id_taikhoan if teacher.tai_khoan else None

        # Tạo đối tượng GiaoVienResponse từ dữ liệu đã xử lý
        teacher_data = schemas.GiaoVienResponse(
            id_gv=teacher.id_gv,
            ten_gv=teacher.ten_gv,
            gioitinh_gv=teacher.gioitinh_gv,
            ngaysinh_gv=teacher.ngaysinh_gv,
            diachi_gv=teacher.diachi_gv,
            sdt_gv=teacher.sdt_gv,
            email_gv=teacher.email_gv,
            tai_khoan_quyen=tai_khoan_quyen,
            lop_hoc_ten=lop_hoc_ten,
            id_taikhoan=id_taikhoan
        )

        result.append(teacher_data)

    return result


def get_teacher_by_id(db: Session, teacher_id: int) -> schemas.GiaoVienResponse:
    # Truy vấn giáo viên theo ID
    teacher = db.query(models.GiaoVien).filter(models.GiaoVien.id_gv == teacher_id).options(
        joinedload(models.GiaoVien.tai_khoan),
        joinedload(models.GiaoVien.lop_hocs)
    ).first()

    # Kiểm tra nếu không tìm thấy giáo viên
    if teacher is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy giáo viên")

    # Lấy thông tin quyền tài khoản từ bảng TaiKhoan
    tai_khoan_quyen = teacher.tai_khoan.quyen if teacher.tai_khoan else None

    # Lấy danh sách tên lớp học từ bảng LopHoc
    lop_hoc_ten = [lop.lophoc for lop in teacher.lop_hocs] if teacher.lop_hocs else []

    # Lấy id_taikhoan từ bảng TaiKhoan
    id_taikhoan = teacher.tai_khoan.id_taikhoan if teacher.tai_khoan else None

    # Tạo đối tượng GiaoVienResponse từ dữ liệu đã xử lý
    teacher_data = schemas.GiaoVienResponse(
        id_gv=teacher.id_gv,
        ten_gv=teacher.ten_gv,
        gioitinh_gv=teacher.gioitinh_gv,
        ngaysinh_gv=teacher.ngaysinh_gv,
        diachi_gv=teacher.diachi_gv,
        sdt_gv=teacher.sdt_gv,
        email_gv=teacher.email_gv,
        tai_khoan_quyen=tai_khoan_quyen,
        lop_hoc_ten=lop_hoc_ten,
        id_taikhoan=id_taikhoan
    )

    return teacher_data


def create_teacher(db: Session, teacher: schemas.GiaoVienCreate):
    # Kiểm tra xem tài khoản đã tồn tại chưa
    existing_account = db.query(models.TaiKhoan).filter(models.TaiKhoan.taikhoan == teacher.taikhoan).first()
    if existing_account:
        raise HTTPException(status_code=400, detail="Tên tài khoản đã tồn tại. Vui lòng chọn tên tài khoản khác.")

    # Tạo tài khoản mới
    new_account = models.TaiKhoan(
        taikhoan=teacher.taikhoan,
        matkhau=hash_password(teacher.matkhau),  # Băm mật khẩu
        quyen=teacher.quyen
    )

    # Thêm tài khoản vào cơ sở dữ liệu
    db.add(new_account)
    db.commit()  # Lưu thay đổi
    db.refresh(new_account)  # Cập nhật đối tượng tài khoản với ID mới

    # Tạo giáo viên mới
    new_teacher = models.GiaoVien(
        ten_gv=teacher.ten_gv,
        gioitinh_gv=teacher.gioitinh_gv,
        ngaysinh_gv=teacher.ngaysinh_gv,
        diachi_gv=teacher.diachi_gv,
        sdt_gv=teacher.sdt_gv,
        email_gv=teacher.email_gv,
        id_taikhoan=new_account.id_taikhoan  # Gắn khóa ngoại với tài khoản
    )

    # Thêm giáo viên vào cơ sở dữ liệu
    db.add(new_teacher)
    try:
        db.commit()  # Lưu thay đổi
        db.refresh(new_teacher)  # Cập nhật đối tượng giáo viên với ID mới
    except Exception as e:
        db.rollback()  # Hoàn tác nếu có lỗi
        raise HTTPException(status_code=400, detail=str(e))  # Thông báo lỗi

    return schemas.GiaoVienResponse(
        id_gv=new_teacher.id_gv,
        ten_gv=new_teacher.ten_gv,
        gioitinh_gv=new_teacher.gioitinh_gv,
        ngaysinh_gv=new_teacher.ngaysinh_gv,
        diachi_gv=new_teacher.diachi_gv,
        sdt_gv=new_teacher.sdt_gv,
        email_gv=new_teacher.email_gv,
        tai_khoan_quyen=new_account.quyen,
        lop_hoc_ten=[],  # Có thể cập nhật sau
        id_taikhoan=new_account.id_taikhoan
    )


def update_teacher(db: Session, teacher_id: int, teacher: schemas.GiaoVienUpdate):
    # Lấy thông tin giáo viên từ cơ sở dữ liệu
    db_teacher = db.query(models.GiaoVien).filter(models.GiaoVien.id_gv == teacher_id).first()

    if not db_teacher:
        raise HTTPException(status_code=404, detail="Giáo viên không tồn tại.")

    # Cập nhật thông tin giáo viên từ thông tin nhận được
    for key, value in teacher.dict(exclude={"quyen", "lop_hoc_ten"}).items():
        if value is not None:
            setattr(db_teacher, key, value)

    # Khởi tạo db_account với giá trị None
    db_account = None

    # Cập nhật quyền nếu có
    if teacher.quyen is not None:
        # Lấy tài khoản liên kết với giáo viên
        db_account = db.query(models.TaiKhoan).filter(
            models.TaiKhoan.id_taikhoan == db_teacher.id_taikhoan).first()

        if db_account is None:
            raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản tương ứng.")

        # Cập nhật quyền tài khoản
        db_account.quyen = teacher.quyen

    # Lưu thay đổi vào cơ sở dữ liệu
    db.commit()

    # Chuyển đổi đối tượng giáo viên thành dạng dữ liệu trả về
    teacher_data = schemas.GiaoVienResponse(  # Đảm bảo bạn sử dụng GiaoVienResponse
        id_gv=db_teacher.id_gv,
        ten_gv=db_teacher.ten_gv,
        gioitinh_gv=db_teacher.gioitinh_gv,
        ngaysinh_gv=db_teacher.ngaysinh_gv,
        diachi_gv=db_teacher.diachi_gv,
        sdt_gv=db_teacher.sdt_gv,
        email_gv=db_teacher.email_gv,
        tai_khoan_quyen=db_account.quyen if db_account else None,
        lop_hoc_ten=[],  # Có thể cập nhật danh sách lớp học nếu cần
        id_taikhoan=db_teacher.id_taikhoan
    )

    return teacher_data


def delete_teacher(db: Session, teacher_id: int):
    # Lấy thông tin giáo viên dựa vào ID
    db_teacher = db.query(models.GiaoVien).filter(models.GiaoVien.id_gv == teacher_id).first()

    if db_teacher is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy giáo viên")

    # Lấy tài khoản của giáo viên
    db_account = db.query(models.TaiKhoan).filter(models.TaiKhoan.id_taikhoan == db_teacher.id_taikhoan).first()

    # Xóa giáo viên và tài khoản
    db.delete(db_teacher)
    if db_account:
        db.delete(db_account)

    db.commit()


# =======================
# Student CRUD Functions
# =======================
def get_all_students(db: Session):
    return db.query(models.HocSinh).all()


def get_student_by_id(db: Session, student_id: int):
    student = db.query(models.HocSinh).filter(models.HocSinh.id_hs == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy học sinh")
    return student


def create_student(db: Session, student: schemas.HocSinhCreate):
    new_account = models.TaiKhoan(
        taikhoan=student.taikhoan,
        matkhau=hash_password(student.matkhau),
        quyen=2
    )

    db.add(new_account)
    db.commit()
    db.refresh(new_account)

    new_student = models.HocSinh(
        ten_hs=student.ten_hs,
        gioitinh_hs=student.gioitinh_hs,
        ngaysinh_hs=student.ngaysinh_hs,
        id_taikhoan=new_account.id_taikhoan
    )

    db.add(new_student)
    try:
        db.commit()
        db.refresh(new_student)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return new_student


def update_student(db: Session, student_id: int, student: schemas.HocSinhUpdate):
    db_student = get_student_by_id(db, student_id)

    for key, value in student.dict(exclude_unset=True).items():
        if value is not None:
            setattr(db_student, key, value)

    db.commit()
    db.refresh(db_student)
    return db_student


def delete_student(db: Session, student_id: int):
    db_student = get_student_by_id(db, student_id)
    db_account = db.query(models.TaiKhoan).filter(models.TaiKhoan.id_taikhoan == db_student.id_taikhoan).first()

    if db_account:
        db.delete(db_account)

    db.delete(db_student)
    db.commit()


# =======================
# Class CRUD Functions
# =======================
def get_all_classes(db: Session):
    return db.query(models.LopHoc).options(
        joinedload(models.LopHoc.giao_vien),
        joinedload(models.LopHoc.nam_hoc)
    ).all()


def get_class_by_id(db: Session, class_id: int):
    cls = db.query(models.LopHoc).options(
        joinedload(models.LopHoc.giao_vien),
        joinedload(models.LopHoc.nam_hoc)
    ).filter(models.LopHoc.id_lh == class_id).first()
    if cls is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học")
    return cls


def create_class(db: Session, class_: schemas.LopHocCreate):
    # Tìm giáo viên dựa trên tên (nếu được cung cấp)
    giao_vien = None
    if class_.ten_gv:
        giao_vien = db.query(models.GiaoVien).filter(models.GiaoVien.ten_gv == class_.ten_gv).first()
        if not giao_vien:
            raise HTTPException(status_code=404, detail="Không tìm thấy giáo viên")

    # Tìm năm học
    nam_hoc = db.query(models.NamHoc).filter(models.NamHoc.namhoc == class_.namhoc).first()
    if not nam_hoc:
        raise HTTPException(status_code=404, detail="Không tìm thấy năm học")

    new_class = models.LopHoc(
        lophoc=class_.lophoc,
        giao_vien=giao_vien,
        nam_hoc=nam_hoc
    )
    db.add(new_class)
    try:
        db.commit()
        db.refresh(new_class)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return new_class


def update_class(db: Session, class_id: int, class_: schemas.LopHocUpdate):
    db_class = get_class_by_id(db, class_id)

    for key, value in class_.dict(exclude_unset=True).items():
        if value is not None:
            setattr(db_class, key, value)

    db.commit()
    db.refresh(db_class)
    return db_class


def delete_class(db: Session, class_id: int):
    db_class = get_class_by_id(db, class_id)
    db.delete(db_class)
    db.commit()


# =======================
# Academic Year CRUD Functions
# =======================
def get_academic_years(db: Session):
    academic_years = db.query(models.NamHoc).all()
    if not academic_years:
        raise HTTPException(status_code=404, detail="Không tìm thấy năm học nào")
    return academic_years


def get_academic_year_by_id(db: Session, year_id: int):
    academic_year = db.query(models.NamHoc).filter(models.NamHoc.id_nh == year_id).first()
    if not academic_year:
        raise HTTPException(status_code=404, detail="Không tìm thấy năm học")
    return academic_year


def create_academic_year(db: Session, year_data: schemas.NamHocCreate):
    new_year = models.NamHoc(namhoc=year_data.namhoc)
    db.add(new_year)
    db.commit()
    db.refresh(new_year)
    return new_year


def update_academic_year(db: Session, year_id: int, year_data: schemas.NamHocUpdate):
    academic_year = get_academic_year_by_id(db, year_id)
    academic_year.namhoc = year_data.namhoc
    db.commit()
    db.refresh(academic_year)
    return academic_year


def delete_academic_year(db: Session, year_id: int):
    academic_year = get_academic_year_by_id(db, year_id)
    db.delete(academic_year)
    db.commit()


# =======================
# Parent CRUD Functions
# =======================
def get_all_parents(db: Session):
    return db.query(models.PhuHuynh).all()


def get_parent_by_id(db: Session, parent_id: int):
    parent = db.query(models.PhuHuynh).filter(models.PhuHuynh.id_ph == parent_id).first()
    if parent is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy phụ huynh")
    return parent


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


def update_parent(db: Session, parent_id: int, parent: schemas.PhuHuynhUpdate):
    db_parent = get_parent_by_id(db, parent_id)

    for key, value in parent.dict().items():
        if value is not None:
            setattr(db_parent, key, value)

    db.commit()
    db.refresh(db_parent)
    return db_parent


def delete_parent(db: Session, parent_id: int):
    db_parent = get_parent_by_id(db, parent_id)
    db.delete(db_parent)
    db.commit()


# =======================
# Account CRUD Functions
# =======================
def get_all_accounts(db: Session):
    return db.query(models.TaiKhoan).all()


def get_account_by_id(db: Session, account_id: int):
    account = db.query(models.TaiKhoan).filter(models.TaiKhoan.id_taikhoan == account_id).first()
    if account is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản")
    return account


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


def update_account(db: Session, account_id: int, account: schemas.TaiKhoanUpdate):
    db_account = get_account_by_id(db, account_id)

    for key, value in account.dict().items():
        if value is not None:
            setattr(db_account, key, value)

    db.commit()
    db.refresh(db_account)
    return db_account


def delete_account(db: Session, account_id: int):
    db_account = get_account_by_id(db, account_id)
    db.delete(db_account)
    db.commit()
