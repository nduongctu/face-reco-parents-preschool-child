from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Body
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Time
from sqlalchemy.orm import sessionmaker
from typing import List, Optional
from backend import models, schemas
from backend.config import settings
from backend import crud
from passlib.context import CryptContext
from datetime import datetime, date
import logging
import shutil
import os
import base64
from io import BytesIO
from PIL import Image
from sklearn.metrics.pairwise import euclidean_distances
from collections import Counter
import numpy as np
from fastapi.responses import JSONResponse

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


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
        raise e

    # Các route API học sinh


@router.get("/students", response_model=List[schemas.HocSinhResponse])
def get_all_students(db: Session = Depends(get_db)):
    students = crud.get_all_students(db)
    if not students:
        raise HTTPException(status_code=404, detail="Không có học sinh nào")
    return students


@router.get("/students_gv/{id_gv}", response_model=List[schemas.HocSinhResponse])
def get_students_by_teacher(id_gv: int, db: Session = Depends(get_db)):
    students = crud.get_students_by_teacher(db, id_gv)
    if not students:
        raise HTTPException(status_code=404, detail="Không có học sinh nào thuộc giáo viên này")
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
@router.get("/students/{student_id}/parents", response_model=List[schemas.PhuHuynhHocSinhResponse])
def read_parents(student_id: int, db: Session = Depends(get_db)):
    parents = crud.get_parent_hoc_sinh(db, student_id)
    return parents


@router.get("/parents/{parent_id}", response_model=schemas.PhuHuynhFullResponse)
def get_parent_by_id(parent_id: int, db: Session = Depends(get_db)):
    parent = crud.get_parent_by_id(db, parent_id)
    if not parent:
        raise HTTPException(status_code=404, detail="Không tìm thấy phụ huynh")
    return schemas.PhuHuynhFullResponse.from_orm(parent)


#
#
# @router.post("/parents", response_model=PhuHuynhResponse)
# def create_parent(parent_data: PhuHuynhCreate, db: Session = Depends(get_db)):
#     return PhuHuynhResponse.from_orm(crud.create_parent(db, parent_data))
#

@router.put("/parents/{parent_id}", response_model=schemas.PhuHuynhFullResponse)
def update_parent_endpoint(
        parent_id: int,
        parent: schemas.PhuHuynhFullUpdate = Body(...),
        db: Session = Depends(get_db)
):
    return crud.update_parent(db, parent_id, parent)


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
@router.get("/accounts/{account_id}", response_model=schemas.TaiKhoanResponse)
def get_account_by_id(account_id: int, db: Session = Depends(get_db)):
    account = crud.get_account_by_id(db, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản")

    return schemas.TaiKhoanResponse.from_orm(account)


#
#
# @router.post("/accounts", response_model=TaiKhoanResponse)
# def create_account(account_data: TaiKhoanCreate, db: Session = Depends(get_db)):
#     return TaiKhoanResponse.from_orm(crud.create_account(db, account_data))
#
#
@router.put("/accounts/{account_id}", response_model=schemas.TaiKhoanResponse)
def update_account(account_id: int, account_data: schemas.TaiKhoanUpdate, db: Session = Depends(get_db)):
    db_account = crud.update_account(db, account_id, account_data)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản")
    return schemas.TaiKhoanResponse.from_orm(db_account)


@router.put("/accounts/username/{username}", response_model=schemas.TaiKhoanResponse)
def update_account_by_username(username: str, account_data: schemas.TaiKhoanUpdate, db: Session = Depends(get_db)):
    db_account = crud.get_account_by_username(db, username)

    if db_account is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản")

    if account_data.matkhau:
        account_data.matkhau = pwd_context.hash(account_data.matkhau)  # Băm mật khẩu mới

    # Cập nhật các trường khác
    for key, value in account_data.dict().items():
        if value is not None:
            setattr(db_account, key, value)

    # Lưu thay đổi vào cơ sở dữ liệu
    db.commit()
    db.refresh(db_account)

    return schemas.TaiKhoanResponse.from_orm(db_account)


@router.post("/images/giao-vien/")
async def upload_teacher_image(id_gv: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    return await crud.upload_teacher_image(db, id_gv, file)


@router.get("/images/giao-vien/{id_gv}/", response_model=schemas.TeacherImageResponse)
def get_teacher_image(id_gv: int, db: Session = Depends(get_db)):
    image = crud.get_teacher_image(db, id_gv)

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    image_url = f"http://localhost:8000/{image.image_path}"

    return schemas.TeacherImageResponse(id_gv=image.id_gv, image_path=image_url)


@router.put("/images/hoc-sinh/{id_hs}/", response_model=schemas.StudentImageResponse)
async def update_student_image(
        id_hs: int,
        file: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    directory = "images/hoc_sinh"
    os.makedirs(directory, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_location = f"{directory}/{timestamp}_{file.filename}"

    # Lưu file hình ảnh
    try:
        with open(file_location, "wb") as f:
            f.write(await file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Không thể lưu hình ảnh: {str(e)}")

    try:
        updated_image = await crud.update_student_image(db, id_hs, file_location)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Có lỗi xảy ra khi cập nhật hình ảnh: {str(e)}")

    if not updated_image:
        raise HTTPException(status_code=404, detail="Học sinh không tồn tại hoặc không thể cập nhật hình ảnh")

    return updated_image


@router.post("/images/hoc-sinh/")
async def upload_student_image(id_hs: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    return await crud.upload_student_image(db, id_hs, file)


@router.get("/images/hoc-sinh/{id_hs}/", response_model=schemas.StudentImageResponse)
def get_student_image(id_hs: int, db: Session = Depends(get_db)):
    image = crud.get_student_image(db, id_hs)

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    image_url = f"http://localhost:8000/{image.image_path}"

    return schemas.StudentImageResponse(id_hs=image.id_hs, image_path=image_url)


@router.post("/images/phu-huynh/{id_ph}/")
async def upload_parent_image(id_ph: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    return await crud.upload_parent_image(db, id_ph, file)


@router.get("/images/phu-huynh/{id_ph}/", response_model=List[schemas.PhuHuynhImageResponse])
def get_all_parent_images(id_ph: int, db: Session = Depends(get_db)):
    try:
        images = crud.get_all_images_for_parent(db, id_ph)
        if not images:
            raise HTTPException(status_code=404, detail="Không tìm thấy ảnh nào cho phụ huynh này")

        # Tạo URL cho tất cả ảnh
        for image in images:
            image.image_path = f"http://localhost:8000/{image.image_path}"

        return images
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")


@router.delete("/images/phu-huynh/{id_image}/")
async def remove_parent_image(id_image: int, db: Session = Depends(get_db)):
    try:
        result = await crud.remove_parent_image(db, id_image)
        return {"detail": "Ảnh đã được xóa thành công"}
    except HTTPException as e:
        raise e
    except Exception as e:
        # Xử lý lỗi hệ thống khác
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")


@router.post("/create", response_model=schemas.DiemDanhResponseWithMessage)
async def create_diemdanh(
        diem_danh_data: schemas.DiemDanhCreate,
        db: Session = Depends(get_db)
):
    try:
        # Kiểm tra xem học sinh đã có bản ghi điểm danh trong ngày này chưa
        existing_record = db.query(models.DiemDanh).filter(
            models.DiemDanh.id_hs == diem_danh_data.id_hs,
            models.DiemDanh.ngay == diem_danh_data.ngay
        ).first()

        if existing_record:
            # Nếu đã có bản ghi, trả về thông báo rằng học sinh đã được điểm danh
            return schemas.DiemDanhResponseWithMessage(
                message="Học sinh đã được điểm danh trong ngày hôm nay.",
                data=schemas.DiemDanhResponse(
                    id=existing_record.id,
                    id_hs=existing_record.id_hs,
                    id_lh=existing_record.id_lh,
                    ngay=existing_record.ngay,
                    gio_vao=existing_record.gio_vao,
                    gio_ra=existing_record.gio_ra,
                    id_ph_don=existing_record.id_ph_don
                )
            )
        else:
            # Nếu chưa có bản ghi, tạo mới
            new_diemdanh = models.DiemDanh(
                id_hs=diem_danh_data.id_hs,
                id_lh=diem_danh_data.id_lh,
                ngay=diem_danh_data.ngay,
                gio_vao=diem_danh_data.gio_vao
            )
            db.add(new_diemdanh)
            db.commit()  # Lưu vào cơ sở dữ liệu
            db.refresh(new_diemdanh)  # Làm mới đối tượng để lấy ID

            # Trả về đối tượng DiemDanhResponse trong DiemDanhResponseWithMessage
            return schemas.DiemDanhResponseWithMessage(
                message="Điểm danh thành công.",
                data=schemas.DiemDanhResponse(
                    id=new_diemdanh.id,
                    id_hs=new_diemdanh.id_hs,
                    id_lh=new_diemdanh.id_lh,
                    ngay=new_diemdanh.ngay,
                    gio_vao=new_diemdanh.gio_vao,
                    gio_ra=new_diemdanh.gio_ra,
                    id_ph_don=new_diemdanh.id_ph_don  # Nếu có trường này trong mô hình
                )
            )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Không thể tạo điểm danh: {str(e)}")


@router.post("/recognize", response_model=schemas.RecognitionResult)
async def recognize(
        frame: dict,
        id_hs_list: list[int],
        euclid_threshold: float,
        db: Session = Depends(get_db)
):
    try:
        # Giải mã frame từ base64 thành ảnh
        frame_data = frame.get("frame")
        if not frame_data:
            raise HTTPException(status_code=400, detail="Không có frame trong yêu cầu")

        image_data = frame_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        image = Image.open(BytesIO(image_bytes))
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        temp_image_path = "temp_image.jpg"
        image.save(temp_image_path)

        # Trích xuất vector từ ảnh
        input_vector = await crud.calculate_vector(temp_image_path)

        # Lấy vector của phụ huynh từ id_hs_list
        vectors = []
        for id_hs in id_hs_list:
            vectors.extend(await crud.get_vectors_by_student_id(db, id_hs))

        # Danh sách để lưu các vector phù hợp
        distances = []
        for vector_info in vectors:
            vector = np.array(vector_info['vector'])
            distance = euclidean_distances(input_vector.reshape(1, -1), vector.reshape(1, -1))[0][0]
            if distance < euclid_threshold:
                distances.append({
                    "id_ph": vector_info['id_ph'],
                    "image_path": vector_info['image_path'],
                    "distance": distance
                })

        if not distances:
            return JSONResponse(content={"success": False, "message": "Không có vector nào dưới ngưỡng."})

        # Tìm vector gần nhất và kiểm tra tần suất xuất hiện của `id_ph`
        top_5_matches = sorted(distances, key=lambda x: x['distance'])[:5]
        id_ph_counts = Counter(match['id_ph'] for match in top_5_matches)
        common_id_ph = [id_ph for id_ph, count in id_ph_counts.items() if count >= 2]

        # Chọn id_ph đón
        if common_id_ph:
            best_match_id = common_id_ph[0]
            best_match = next(match for match in top_5_matches if match['id_ph'] == best_match_id)
        else:
            best_match = top_5_matches[0]

        recognized_id_ph = best_match['id_ph']

        # Kiểm tra bản ghi điểm danh của học sinh trong ngày hôm nay
        today = datetime.now().date()
        current_time = datetime.now().time()

        diem_danh_record = db.query(models.DiemDanh).filter(
            models.DiemDanh.id_hs == id_hs_list[0],
            models.DiemDanh.ngay == today
        ).first()

        # Nếu bản ghi đã có `gio_ra`, trả về lỗi
        if diem_danh_record:
            if diem_danh_record.gio_ra is not None:
                raise HTTPException(status_code=400, detail="Học sinh đã được đón trong ngày hôm nay.")

            # Nếu chưa có `gio_ra`, cập nhật giờ ra và id_ph_don
            diem_danh_record.id_ph_don = recognized_id_ph
            diem_danh_record.gio_ra = current_time
        else:
            # Nếu chưa có bản ghi, trả về lỗi hoặc tạo mới nếu muốn
            raise HTTPException(status_code=404, detail="Không tìm thấy bản ghi điểm danh cho học sinh trong ngày.")

        db.commit()

        # Lấy tên phụ huynh từ cơ sở dữ liệu
        parent_record = db.query(models.PhuHuynh).filter(models.PhuHuynh.id_ph == recognized_id_ph).first()
        parent_name = parent_record.ten_ph if parent_record else "Không xác định"

        # Trả về kết quả nhận dạng
        return schemas.RecognitionResult(
            success=True,
            message=f"Nhận dạng thành công! {parent_name}",
            data={
                "id_ph": recognized_id_ph,
                "image_path": best_match['image_path'],
                "distance": best_match['distance']
            }
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")


@router.get("/diem-danh", response_model=schemas.DiemDanhResponseList)
async def get_diem_danh_api(
        id_lh: int,
        ngay: str,
        db: Session = Depends(get_db)
):
    try:
        ngay_date = datetime.strptime(ngay, "%Y-%m-%d").date()

        diem_danh_details = crud.get_diem_danh(db, id_lh, ngay_date)

        # Nếu không có kết quả nào, trả về lỗi 404
        if not diem_danh_details:
            raise HTTPException(status_code=404, detail="Không tìm thấy điểm danh cho lớp học và ngày đã chỉ định.")

        return schemas.DiemDanhResponseList(data=diem_danh_details)

    except ValueError:
        raise HTTPException(status_code=400, detail="Ngày không đúng định dạng. Định dạng đúng là YYYY-MM-DD.")
