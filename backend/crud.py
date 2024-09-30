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
def get_all_students(db: Session) -> List[schemas.HocSinhResponse]:
    students = db.query(models.HocSinh).options(
        joinedload(models.HocSinh.tai_khoan),
        joinedload(models.HocSinh.lop_hoc),
        joinedload(models.HocSinh.phu_huynhs)
    ).all()

    result = []
    for student in students:
        lop_hoc_ten = student.lop_hoc.lophoc if student.lop_hoc else 'Chưa có lớp'

        # Lấy danh sách thông tin phụ huynh từ bảng PhuHuynh_HocSinh
        phu_huynh_info = [
            {
                "id_ph": phu_huynh.phu_huynh.id_ph,  # Thêm id_ph ở đây
                "ten_ph": phu_huynh.phu_huynh.ten_ph,
                "quanhe": phu_huynh.quanhe,
                "gioitinh_ph": phu_huynh.phu_huynh.gioitinh_ph  # Thêm giới tính phụ huynh ở đây

            }
            for phu_huynh in student.phu_huynhs
        ]

        id_taikhoan = student.tai_khoan.id_taikhoan if student.tai_khoan else None

        student_data = schemas.HocSinhResponse(
            id_hs=student.id_hs,
            ten_hs=student.ten_hs,
            gioitinh_hs=student.gioitinh_hs,
            ngaysinh_hs=student.ngaysinh_hs,
            lop_hoc_ten=lop_hoc_ten,
            phu_huynh=phu_huynh_info,
            id_taikhoan=id_taikhoan
        )

        result.append(student_data)

    return result


def get_student_by_id(db: Session, student_id: int) -> schemas.HocSinhResponse:
    student = db.query(models.HocSinh).options(
        joinedload(models.HocSinh.tai_khoan),
        joinedload(models.HocSinh.lop_hoc),
        joinedload(models.HocSinh.phu_huynhs)
    ).filter(models.HocSinh.id_hs == student_id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Học sinh không tìm thấy")

    lop_hoc_ten = student.lop_hoc.lophoc if student.lop_hoc else 'Chưa có lớp'

    # Lấy thông tin phụ huynh, bao gồm cả giới tính
    phu_huynh_info = [
        {
            "id_ph": phu_huynh.phu_huynh.id_ph,  # ID phụ huynh
            "ten_ph": phu_huynh.phu_huynh.ten_ph,
            "quanhe": phu_huynh.quanhe,
            "gioitinh_ph": phu_huynh.phu_huynh.gioitinh_ph  # Thêm giới tính phụ huynh ở đây
        }
        for phu_huynh in student.phu_huynhs
    ]

    id_taikhoan = student.tai_khoan.id_taikhoan if student.tai_khoan else None

    student_data = schemas.HocSinhResponse(
        id_hs=student.id_hs,
        ten_hs=student.ten_hs,
        gioitinh_hs=student.gioitinh_hs,
        ngaysinh_hs=student.ngaysinh_hs,
        lop_hoc_ten=lop_hoc_ten,
        phu_huynh=phu_huynh_info,
        id_taikhoan=id_taikhoan
    )

    return student_data


def create_student_with_parents(db: Session, student_data: schemas.HocSinhCreate):
    # 1. Tạo tài khoản cho học sinh
    existing_account = db.query(models.TaiKhoan).filter(models.TaiKhoan.taikhoan == student_data.taikhoan).first()
    if existing_account:
        raise HTTPException(status_code=400, detail="Tài khoản đã tồn tại")

    new_account = models.TaiKhoan(
        taikhoan=student_data.taikhoan,
        matkhau=hash_password(student_data.matkhau),
        quyen=student_data.quyen
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)

    # 2. Tạo học sinh
    new_student = models.HocSinh(
        ten_hs=student_data.ten_hs,
        gioitinh_hs=student_data.gioitinh_hs,
        ngaysinh_hs=student_data.ngaysinh_hs,
        id_taikhoan=new_account.id_taikhoan
    )
    db.add(new_student)
    db.commit()  # Có thể giữ lại commit này để đảm bảo học sinh được lưu thành công
    db.refresh(new_student)

    # 3. Tạo thông tin phụ huynh và liên kết với học sinh
    for phu_huynh_data in student_data.phu_huynh:
        new_parent = models.PhuHuynh(
            ten_ph=phu_huynh_data.ten_ph,
            gioitinh_ph=phu_huynh_data.gioitinh_ph
        )
        db.add(new_parent)
        db.commit()  # Lưu phụ huynh trước khi tạo mối quan hệ
        db.refresh(new_parent)  # Lấy ID của phụ huynh đã lưu

        # 4. Tạo quan hệ giữa học sinh và phụ huynh
        new_relation = models.PhuHuynh_HocSinh(
            id_hs=new_student.id_hs,  # ID học sinh
            id_ph=new_parent.id_ph,  # ID phụ huynh
            quanhe=phu_huynh_data.quanhe
        )
        db.add(new_relation)

    # 5. Commit cuối cùng cho các quan hệ phụ huynh
    db.commit()

    return new_student


def update_student_with_parents(db: Session, student_id: int, student_data: schemas.HocSinhUpdate) -> Optional[schemas.HocSinhResponse]:
    student = db.query(models.HocSinh).filter(models.HocSinh.id_hs == student_id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Học sinh không tồn tại")

    # Cập nhật thông tin học sinh
    if student_data.ten_hs is not None:
        student.ten_hs = student_data.ten_hs
    if student_data.gioitinh_hs is not None:
        student.gioitinh_hs = student_data.gioitinh_hs
    if student_data.ngaysinh_hs is not None:
        student.ngaysinh_hs = student_data.ngaysinh_hs

    # Cập nhật lớp học nếu có ID lớp học
    if student_data.lop_hoc_ten is not None:
        # Lấy ID lớp học từ student_data
        lop_hoc_id = int(student_data.lop_hoc_ten)  # Chuyển đổi ID lớp học thành số nguyên
        lop_hoc = db.query(models.LopHoc).filter(models.LopHoc.id_lh == lop_hoc_id).first()  # Tìm lớp học theo ID
        if lop_hoc:
            student.id_lh = lop_hoc.id_lh  # Cập nhật ID lớp học
        else:
            raise HTTPException(status_code=404, detail="Lớp học không tồn tại")  # Lớp học không tồn tại

    # Lấy danh sách ID phụ huynh đã được gửi từ frontend
    updated_parent_ids = {phu_huynh.id_ph for phu_huynh in student_data.phu_huynh if phu_huynh.id_ph}

    # Xóa các phụ huynh không còn trong danh sách gửi từ frontend
    current_relations = db.query(models.PhuHuynh_HocSinh).filter(models.PhuHuynh_HocSinh.id_hs == student_id).all()

    for relation in current_relations:
        if relation.id_ph not in updated_parent_ids:
            db.delete(relation)  # Xóa quan hệ giữa học sinh và phụ huynh

    # Cập nhật thông tin phụ huynh
    if student_data.phu_huynh is not None:
        for phu_huynh_data in student_data.phu_huynh:
            if phu_huynh_data.id_ph:  # Phụ huynh đã tồn tại
                existing_parent = db.query(models.PhuHuynh).filter(
                    models.PhuHuynh.id_ph == phu_huynh_data.id_ph).first()

                if existing_parent:
                    # Cập nhật tên phụ huynh nếu có
                    if phu_huynh_data.ten_ph is not None:
                        existing_parent.ten_ph = phu_huynh_data.ten_ph

                    # Cập nhật quan hệ giữa phụ huynh và học sinh
                    existing_relation = db.query(models.PhuHuynh_HocSinh).filter(
                        models.PhuHuynh_HocSinh.id_hs == student.id_hs,
                        models.PhuHuynh_HocSinh.id_ph == existing_parent.id_ph
                    ).first()

                    if existing_relation and phu_huynh_data.quanhe is not None:
                        existing_relation.quanhe = phu_huynh_data.quanhe

            else:  # Thêm phụ huynh mới nếu không có ID
                new_parent = models.PhuHuynh(
                    ten_ph=phu_huynh_data.ten_ph,
                    gioitinh_ph=phu_huynh_data.gioitinh_ph
                )
                db.add(new_parent)
                db.commit()  # Lưu lại để có ID cho phụ huynh mới
                db.refresh(new_parent)

                # Tạo quan hệ giữa phụ huynh mới và học sinh
                new_relation = models.PhuHuynh_HocSinh(
                    id_hs=student.id_hs,
                    id_ph=new_parent.id_ph,
                    quanhe=phu_huynh_data.quanhe
                )
                db.add(new_relation)

    db.commit()  # Lưu tất cả các thay đổi
    db.refresh(student)  # Làm mới đối tượng học sinh để đảm bảo phản ánh thay đổi
    return student  # Trả về đối tượng học sinh đã cập nhật


def delete_student(db: Session, student_id: int):
    # Lấy thông tin học sinh
    db_student = db.query(models.HocSinh).filter(models.HocSinh.id_hs == student_id).first()

    if db_student is None:
        raise HTTPException(status_code=404, detail="Học sinh không tồn tại!")

    # Lấy danh sách phụ huynh liên kết với học sinh này
    parent_relations = db.query(models.PhuHuynh_HocSinh).filter(models.PhuHuynh_HocSinh.id_hs == student_id).all()
    parent_ids = [relation.id_ph for relation in parent_relations]

    # Xóa các quan hệ giữa phụ huynh và học sinh
    if parent_relations:
        db.query(models.PhuHuynh_HocSinh).filter(models.PhuHuynh_HocSinh.id_hs == student_id).delete(
            synchronize_session=False)

    # Xóa phụ huynh nếu không có mối quan hệ nào khác
    if parent_ids:
        db.query(models.PhuHuynh).filter(models.PhuHuynh.id_ph.in_(parent_ids)).delete(synchronize_session=False)

    # Lấy tài khoản liên kết
    db_account = db.query(models.TaiKhoan).filter(models.TaiKhoan.id_taikhoan == db_student.id_taikhoan).first()

    # Xóa tài khoản nếu có
    if db_account:
        db.delete(db_account)

    # Xóa học sinh
    db.delete(db_student)
    db.commit()


# =======================
# Class CRUD Functions
# =======================
def get_all_classes(db: Session):
    classes = db.query(models.LopHoc).options(
        joinedload(models.LopHoc.giao_vien),
        joinedload(models.LopHoc.nam_hoc),
        joinedload(models.LopHoc.hoc_sinh)  # Tải trước học sinh
    ).all()

    result = []
    for cls in classes:
        total_students = len(cls.hoc_sinh)  # Tính tổng số học sinh trong lớp
        class_data = schemas.LopHocBase(
            id_lh=cls.id_lh,
            lophoc=cls.lophoc,
            giao_vien=cls.giao_vien,
            nam_hoc=cls.nam_hoc,
            tong_so_hoc_sinh=total_students  # Gán tổng số học sinh
        )
        result.append(class_data)

    return result


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
