from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, UploadFile
from backend import models, schemas
from passlib.context import CryptContext
from typing import List, Optional
from admin import save_image

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
        joinedload(models.GiaoVien.lop_hoc)  # Load thông tin lớp học
    ).all()

    # Xử lý dữ liệu và chuyển đổi thành mô hình Pydantic
    result = []
    for teacher in teachers:
        # Lấy quyền tài khoản từ bảng TaiKhoan (nếu có)
        tai_khoan_quyen = teacher.tai_khoan.quyen if teacher.tai_khoan else None

        # Lấy tên lớp học từ bảng LopHoc
        lop_hoc_ten = teacher.lop_hoc.lophoc if teacher.lop_hoc else None

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
            lop_hoc_ten=lop_hoc_ten,  # Thêm tên lớp học
            id_taikhoan=id_taikhoan,
            id_lh=teacher.id_lh  # Nếu bạn vẫn muốn giữ id_lh
        )

        result.append(teacher_data)

    return result


def get_teacher_by_id(db: Session, teacher_id: int) -> schemas.GiaoVienResponse:
    # Truy vấn giáo viên theo ID và join với bảng TaiKhoan
    teacher = db.query(models.GiaoVien).filter(models.GiaoVien.id_gv == teacher_id).options(
        joinedload(models.GiaoVien.tai_khoan)
    ).first()

    # Kiểm tra nếu không tìm thấy giáo viên
    if teacher is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy giáo viên")

    # Lấy quyền tài khoản từ bảng TaiKhoan (nếu có)
    tai_khoan_quyen = teacher.tai_khoan.quyen if teacher.tai_khoan else None
    id_taikhoan = teacher.tai_khoan.id_taikhoan if teacher.tai_khoan else None

    # Lấy tên lớp học từ id_lh
    lop_hoc = db.query(models.LopHoc).filter(models.LopHoc.id_lh == teacher.id_lh).first()
    lop_hoc_ten = lop_hoc.lophoc if lop_hoc else None  # Nếu không tìm thấy lớp thì None

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
        lop_hoc_ten=lop_hoc_ten,  # Thêm tên lớp học
        id_taikhoan=id_taikhoan,
        id_lh=teacher.id_lh  # Giữ nguyên id_lh
    )

    return teacher_data


def create_teacher(db: Session, teacher: schemas.GiaoVienCreate) -> schemas.GiaoVienCreateResponse:
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
    db.commit()
    db.refresh(new_account)  # Cập nhật đối tượng tài khoản với ID mới

    # Tạo giáo viên mới và liên kết với tài khoản
    new_teacher = models.GiaoVien(
        ten_gv=teacher.ten_gv,
        gioitinh_gv=teacher.gioitinh_gv,
        ngaysinh_gv=teacher.ngaysinh_gv,
        diachi_gv=teacher.diachi_gv,
        sdt_gv=teacher.sdt_gv,
        email_gv=teacher.email_gv,
        id_taikhoan=new_account.id_taikhoan  # Liên kết tài khoản với giáo viên
    )

    db.add(new_teacher)
    try:
        db.commit()
        db.refresh(new_teacher)  # Cập nhật đối tượng giáo viên với ID mới
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    return schemas.GiaoVienCreateResponse(
        id_gv=new_teacher.id_gv,
        ten_gv=new_teacher.ten_gv,
        gioitinh_gv=new_teacher.gioitinh_gv,
        ngaysinh_gv=new_teacher.ngaysinh_gv,
        diachi_gv=new_teacher.diachi_gv,
        sdt_gv=new_teacher.sdt_gv,
        email_gv=new_teacher.email_gv,
        quyen=new_account.quyen,
        id_taikhoan=new_account.id_taikhoan,
        id_lh=None
    )


def update_teacher(db: Session, teacher_id: int, teacher: schemas.GiaoVienUpdate):
    # Lấy thông tin giáo viên từ cơ sở dữ liệu
    db_teacher = db.query(models.GiaoVien).filter(models.GiaoVien.id_gv == teacher_id).first()

    if not db_teacher:
        raise HTTPException(status_code=404, detail="Giáo viên không tồn tại.")

    # Hiển thị thông tin hiện tại
    print(f"Thông tin giáo viên trước khi cập nhật: {db_teacher}")

    # Cập nhật thông tin giáo viên từ thông tin nhận được
    updated_fields = []  # Danh sách các trường đã được cập nhật

    # Cập nhật các thông tin cơ bản
    for key, value in teacher.dict(exclude={"quyen", "lop_hoc_ten"}).items():
        if value is not None and getattr(db_teacher, key) != value:
            setattr(db_teacher, key, value)
            updated_fields.append(key)  # Ghi nhận trường đã được cập nhật

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
        if db_account.quyen != teacher.quyen:
            db_account.quyen = teacher.quyen
            updated_fields.append("quyen")  # Ghi nhận trường quyền đã được cập nhật

    # Cập nhật lớp học nếu có
    if teacher.id_lh is not None:
        # Kiểm tra xem lớp học có tồn tại trong cơ sở dữ liệu không
        lop_hoc = db.query(models.LopHoc).filter(models.LopHoc.id_lh == teacher.id_lh).first()

        if lop_hoc:
            db_teacher.id_lh = teacher.id_lh  # Cập nhật ID lớp học cho giáo viên
            updated_fields.append("id_lh")  # Ghi nhận trường id_lh đã được cập nhật
        else:
            raise HTTPException(status_code=404, detail="Lớp học không tồn tại.")

    # Kiểm tra có trường nào được cập nhật không
    if updated_fields:
        # Lưu thay đổi vào cơ sở dữ liệu
        db.commit()
        print(f"Các trường đã được cập nhật: {updated_fields}")
    else:
        print("Không có trường nào được cập nhật.")

    # Chuyển đổi đối tượng giáo viên thành dạng dữ liệu trả về
    teacher_data = schemas.GiaoVienResponse(
        id_gv=db_teacher.id_gv,
        ten_gv=db_teacher.ten_gv,
        gioitinh_gv=db_teacher.gioitinh_gv,
        ngaysinh_gv=db_teacher.ngaysinh_gv,
        diachi_gv=db_teacher.diachi_gv,
        sdt_gv=db_teacher.sdt_gv,
        email_gv=db_teacher.email_gv,
        tai_khoan_quyen=db_account.quyen if db_account else None,
        id_taikhoan=db_teacher.id_taikhoan,
        id_lh=db_teacher.id_lh  # Đảm bảo ID lớp học được đưa vào
    )

    # Lấy tên lớp học từ ID lớp học
    if db_teacher.id_lh is not None:
        lop_hoc = db.query(models.LopHoc).filter(models.LopHoc.id_lh == db_teacher.id_lh).first()
        teacher_data.lop_hoc_ten = lop_hoc.lophoc if lop_hoc else None  # Lấy tên lớp học nếu có
    else:
        teacher_data.lop_hoc_ten = None  # Nếu không có ID lớp học, set thành None

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

        # Lấy năm học từ lớp học
        nam_hoc = student.lop_hoc.nam_hoc.namhoc if student.lop_hoc and student.lop_hoc.nam_hoc else 'Chưa có năm học'

        # Thông tin phụ huynh
        phu_huynh_info = [
            {
                "id_ph": phu_huynh.phu_huynh.id_ph,
                "ten_ph": phu_huynh.phu_huynh.ten_ph,
                "quanhe": phu_huynh.quanhe,
                "gioitinh_ph": phu_huynh.phu_huynh.gioitinh_ph
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
            nam_hoc=nam_hoc,  # Gán năm học cho học sinh
            phu_huynh=phu_huynh_info,
            id_taikhoan=id_taikhoan
        )

        result.append(student_data)

    return result


def get_students_by_teacher(db: Session, id_gv: int) -> List[schemas.HocSinhResponse]:
    students = db.query(models.HocSinh).join(models.HocSinh.lop_hoc).join(models.LopHoc.giao_viens).options(
        joinedload(models.HocSinh.tai_khoan),
        joinedload(models.HocSinh.lop_hoc),
        joinedload(models.HocSinh.lop_hoc).joinedload(models.LopHoc.nam_hoc),  # Tải thêm thông tin NamHoc
        joinedload(models.HocSinh.phu_huynhs)
    ).filter(
        models.GiaoVien.id_gv == id_gv  # Lọc theo id giáo viên
    ).all()

    result = []
    for student in students:
        lop_hoc_ten = student.lop_hoc.lophoc if student.lop_hoc else 'Chưa có lớp'
        nam_hoc = student.lop_hoc.nam_hoc.namhoc if student.lop_hoc and student.lop_hoc.nam_hoc else 'Chưa có năm học'

        # Lấy danh sách thông tin phụ huynh từ bảng PhuHuynh_HocSinh
        phu_huynh_info = [
            {
                "id_ph": phu_huynh.phu_huynh.id_ph,
                "ten_ph": phu_huynh.phu_huynh.ten_ph,
                "quanhe": phu_huynh.quanhe,
                "gioitinh_ph": phu_huynh.phu_huynh.gioitinh_ph
            }
            for phu_huynh in student.phu_huynhs
        ]

        id_taikhoan = student.tai_khoan.id_taikhoan if student.tai_khoan else None

        # Tạo dữ liệu cho từng học sinh
        student_data = schemas.HocSinhResponse(
            id_hs=student.id_hs,
            ten_hs=student.ten_hs,
            gioitinh_hs=student.gioitinh_hs,
            ngaysinh_hs=student.ngaysinh_hs,
            lop_hoc_ten=lop_hoc_ten,
            nam_hoc=nam_hoc,  # Thêm thông tin năm học
            phu_huynh=phu_huynh_info,
            id_taikhoan=id_taikhoan
        )

        result.append(student_data)

    return result


def get_student_by_id(db: Session, student_id: int) -> schemas.HocSinhResponse:
    student = db.query(models.HocSinh).options(
        joinedload(models.HocSinh.tai_khoan),
        joinedload(models.HocSinh.lop_hoc),
        joinedload(models.HocSinh.phu_huynhs),
        joinedload(models.HocSinh.lop_hoc).joinedload(models.LopHoc.nam_hoc)  # Thêm để tải năm học
    ).filter(models.HocSinh.id_hs == student_id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Học sinh không tìm thấy")

    # Lấy tên lớp học
    lop_hoc_ten = student.lop_hoc.lophoc if student.lop_hoc else 'Chưa có lớp'

    # Lấy thông tin năm học
    nam_hoc = student.lop_hoc.nam_hoc.namhoc if student.lop_hoc and student.lop_hoc.nam_hoc else 'Chưa có năm học'

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
        nam_hoc=nam_hoc,
        phu_huynh=phu_huynh_info,
        id_taikhoan=id_taikhoan
    )

    return student_data


def create_student_with_parents(db: Session, student_data: schemas.HocSinhCreate):
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

    new_student = models.HocSinh(
        ten_hs=student_data.ten_hs,
        gioitinh_hs=student_data.gioitinh_hs,
        ngaysinh_hs=student_data.ngaysinh_hs,
        id_taikhoan=new_account.id_taikhoan
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    for phu_huynh_data in student_data.phu_huynh:
        new_parent = models.PhuHuynh(
            ten_ph=phu_huynh_data.ten_ph,
            gioitinh_ph=phu_huynh_data.gioitinh_ph
        )
        db.add(new_parent)
        db.commit()
        db.refresh(new_parent)

        new_relation = models.PhuHuynh_HocSinh(
            id_hs=new_student.id_hs,
            id_ph=new_parent.id_ph,
            quanhe=phu_huynh_data.quanhe
        )
        db.add(new_relation)

    db.commit()

    return new_student


def update_student_with_parents(db: Session, student_id: int, student_data: schemas.HocSinhUpdate) -> Optional[
    schemas.HocSinhResponse]:
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
        joinedload(models.LopHoc.giao_viens),
        joinedload(models.LopHoc.nam_hoc),
        joinedload(models.LopHoc.hoc_sinhs)  # Tải trước học sinh
    ).all()

    result = []
    for cls in classes:
        total_students = len(cls.hoc_sinhs)  # Tính tổng số học sinh trong lớp
        class_data = schemas.LopHocBase(
            id_lh=cls.id_lh,
            lophoc=cls.lophoc,
            giao_vien=[gv for gv in cls.giao_viens],  # Danh sách giáo viên
            nam_hoc=cls.nam_hoc,
            tong_so_hoc_sinh=total_students  # Gán tổng số học sinh
        )
        result.append(class_data)

    return result


def get_class_by_id(db: Session, id_lh: int):
    # Tải lớp học cùng với các thực thể liên quan
    cls = db.query(models.LopHoc).options(
        joinedload(models.LopHoc.giao_viens),
        joinedload(models.LopHoc.nam_hoc),
        joinedload(models.LopHoc.hoc_sinhs)  # Tải trước học sinh
    ).filter(models.LopHoc.id_lh == id_lh).first()

    # Trả về None nếu không tìm thấy lớp học
    if cls is None:
        return None

    # Tính tổng số học sinh trong lớp
    total_students = len(cls.hoc_sinhs)

    # Tạo đối tượng LopHocBase với thông tin của lớp học
    class_data = schemas.LopHocBase(
        id_lh=cls.id_lh,
        lophoc=cls.lophoc,
        giao_vien=[gv for gv in cls.giao_viens],  # Danh sách giáo viên
        nam_hoc=cls.nam_hoc,
        tong_so_hoc_sinh=total_students  # Tổng số học sinh
    )

    return class_data


def create_class(db: Session, class_: schemas.LopHocCreate):
    new_class = models.LopHoc(
        lophoc=class_.lophoc,
        id_nh=class_.id_nh
    )

    if class_.id_gv:  # Nếu có danh sách ID giáo viên
        for id_gv in class_.id_gv:
            # Truy vấn giáo viên từ cơ sở dữ liệu
            gv = db.query(models.GiaoVien).filter(models.GiaoVien.id_gv == id_gv).first()
            if gv:
                new_class.giao_viens.append(gv)  # Thêm giáo viên vào lớp

    # Thêm lớp học vào cơ sở dữ liệu
    db.add(new_class)
    db.commit()
    db.refresh(new_class)

    return schemas.LopHocResponse.from_orm(new_class)


def update_class(db: Session, class_id: int, class_data: schemas.LopHocUpdate):
    # Lấy lớp học từ cơ sở dữ liệu dựa trên `class_id`
    db_class = db.query(models.LopHoc).filter(models.LopHoc.id_lh == class_id).first()

    if not db_class:
        raise HTTPException(status_code=404, detail="Class not found")

    # Cập nhật tên lớp học nếu có trong dữ liệu gửi lên
    if class_data.lophoc is not None:
        db_class.lophoc = class_data.lophoc

    # Cập nhật năm học nếu có trong dữ liệu gửi lên
    if class_data.id_nh is not None:
        db_class.id_nh = class_data.id_nh

    # Cập nhật id_lh từ payload
    if class_data.id_lh is not None:
        db_class.id_lh = class_data.id_lh

    # Nếu có danh sách giáo viên gửi lên
    if class_data.id_gv is not None:
        current_teachers = {gv.id_gv for gv in db_class.giao_viens}

        for gv_id in class_data.id_gv:
            if gv_id not in current_teachers:
                teacher = db.query(models.GiaoVien).filter(models.GiaoVien.id_gv == gv_id).first()
                if teacher:
                    db_class.giao_viens.append(teacher)

        for teacher in db_class.giao_viens:
            if teacher.id_gv not in set(class_data.id_gv):
                db_class.giao_viens.remove(teacher)

    db.commit()
    db.refresh(db_class)

    return schemas.LopHocUpdate.from_orm(db_class)


def delete_class(db: Session, class_id: int):
    # Lấy lớp học từ cơ sở dữ liệu
    db_class = db.query(models.LopHoc).filter(models.LopHoc.id_lh == class_id).first()

    if db_class is None:
        raise HTTPException(status_code=404, detail="Lớp học không tồn tại.")

    db.delete(db_class)  # Xóa lớp học
    db.commit()  # Lưu thay đổi

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
        raise HTTPException(status_code=404, detail="Không tìm thấy năm học với ID này")
    return academic_year


def create_academic_year(db: Session, year: schemas.NamHocCreate):
    db_year = models.NamHoc(namhoc=year.namhoc)
    db.add(db_year)
    db.commit()
    db.refresh(db_year)
    return db_year


def update_academic_year(db: Session, year_id: int, year_data: schemas.NamHocUpdate):
    academic_year = db.query(models.NamHoc).filter(models.NamHoc.id_nh == year_id).first()

    if not academic_year:
        raise HTTPException(status_code=404, detail="Năm học không tồn tại")

    if year_data.namhoc is not None:
        academic_year.namhoc = year_data.namhoc

    db.commit()
    db.refresh(academic_year)
    return academic_year


def delete_academic_year(db: Session, year_id: int):
    db_academic_year = db.query(models.NamHoc).filter(models.NamHoc.id_nh == year_id).first()
    if not db_academic_year:
        raise HTTPException(status_code=404, detail="Không tìm thấy năm học")

    db.delete(db_academic_year)
    db.commit()
    return {"detail": "Xóa năm học thành công"}

    # =======================
    # Parent CRUD Functions
    # =======================


def get_all_parents(db: Session):
    return db.query(models.PhuHuynh).all()


def get_parent_by_id(db: Session, parent_id: int):
    # Lấy phụ huynh và thông tin quan hệ với học sinh
    parent = db.query(models.PhuHuynh).options(joinedload(models.PhuHuynh.phu_hoc_sinh)).filter(
        models.PhuHuynh.id_ph == parent_id).first()

    if parent is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy phụ huynh")

    # Tạo danh sách quan hệ từ bảng PhuHuynh_HocSinh
    if parent.phu_hoc_sinh:  # Nếu có mối quan hệ
        quanhe_list = [relationship.quanhe for relationship in parent.phu_hoc_sinh]
        parent.quanhe = ', '.join(quanhe_list)  # Ghép các quan hệ thành chuỗi
    else:
        parent.quanhe = None  # Không có thông tin quan hệ

    return parent


# Lấy thông tin phụ huynh cùng với hình ảnh
def get_full_parent_info(db: Session, parent_id: int) -> schemas.PhuHuynhFullResponse:
    parent = get_parent_by_id(db, parent_id)
    if not parent:
        return None

    image_paths = [image.image_path for image in parent.images] if parent.images else []

    # Trả về đối tượng PhuHuynhFullResponse
    return schemas.PhuHuynhFullResponse(
        id_ph=parent.id_ph,
        ten_ph=parent.ten_ph,
        gioitinh_ph=parent.gioitinh_ph,
        ngay_sinh_ph=parent.ngaysinh_ph,
        sdt_ph=parent.sdt_ph,
        diachi_ph=parent.diachi_ph,
        hinhanh_ph=image_paths
    )


def get_parent_hoc_sinh(db: Session, hs_id: int):
    # Lấy học sinh theo ID
    student = db.query(models.HocSinh).filter(models.HocSinh.id_hs == hs_id).first()

    if student is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy học sinh")

    # Tạo danh sách phụ huynh cho học sinh
    parents = []
    for ph in student.phu_huynhs:  # Lặp qua các đối tượng PhuHuynh_HocSinh
        parent = db.query(models.PhuHuynh).filter(models.PhuHuynh.id_ph == ph.id_ph).first()
        if parent:
            parents.append({
                "id_ph": parent.id_ph,
                "ten_ph": parent.ten_ph,
                "gioitinh_ph": parent.gioitinh_ph,
                "ngaysinh_ph": parent.ngaysinh_ph,
                "sdt_ph": parent.sdt_ph,
                "diachi_ph": parent.diachi_ph,
                "quanhe": ph.quanhe  # Lấy quan hệ từ PhuHuynh_HocSinh
            })

    return parents


def update_parent(db: Session, parent_id: int, parent: schemas.PhuHuynhFullUpdate, files: List[UploadFile] = None):
    db_parent = get_parent_by_id(db, parent_id)

    if not db_parent:
        raise HTTPException(status_code=404, detail="Không tìm thấy phụ huynh")

    for key, value in parent.dict(exclude_unset=True).items():
        setattr(db_parent, key, value)

    if files:
        existing_images = db.query(models.PhuHuynh_Images).filter(models.PhuHuynh_Images.id_ph == parent_id).all()

        for image in existing_images:
            db.delete(image)
            if os.path.exists(image.image_path):
                os.remove(image.image_path)

        for file in files:
            file_location = save_image(file)
            new_image = models.PhuHuynh_Images(id_ph=parent_id, image_path=file_location)
            db.add(new_image)

    db.commit()
    db.refresh(db_parent)

    return db_parent


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


def delete_parent(db: Session, parent_id: int):
    db_parent = get_parent_by_id(db, parent_id)
    db.delete(db_parent)
    db.commit()

    # =======================
    # Account CRUD Functions
    # =======================


def get_all_accounts(db: Session):
    return db.query(models.TaiKhoan).all()


def get_account_by_id(db: Session, account_id: int) -> schemas.TaiKhoanBase:
    # Truy vấn tài khoản từ CSDL
    account = db.query(models.TaiKhoan).filter(models.TaiKhoan.id_taikhoan == account_id).first()

    # Kiểm tra xem tài khoản có tồn tại không
    if account is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản")

    # Trả về dữ liệu theo đúng schema TaiKhoanBase
    return schemas.TaiKhoanBase.from_orm(account)


def get_account_by_username(db: Session, username: str):
    account = db.query(models.TaiKhoan).filter(models.TaiKhoan.taikhoan == username).first()
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

    if account.matkhau is not None:
        # Mã hóa mật khẩu trước khi cập nhật
        account.matkhau = hash_password(account.matkhau)

    for key, value in account.dict().items():
        if value is not None:
            setattr(db_account, key, value)

    db.commit()
    db.refresh(db_account)

    # Trả về tài khoản đã được cập nhật
    return db_account


def delete_account(db: Session, account_id: int):
    db_account = get_account_by_id(db, account_id)
    db.delete(db_account)
    db.commit()
