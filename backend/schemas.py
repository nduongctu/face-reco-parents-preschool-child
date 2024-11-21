from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date, time


# Định nghĩa các lớp Pydantic
class TaiKhoanBase(BaseModel):
    taikhoan: str
    matkhau: str
    quyen: int

    model_config = ConfigDict(from_attributes=True)  # Sử dụng ConfigDict


class PhuHuynhBase(BaseModel):
    id_ph: int
    ten_ph: str

    model_config = ConfigDict(from_attributes=True)  # Sử dụng ConfigDict


class NamHocBase(BaseModel):
    id_nh: int
    namhoc: str

    model_config = ConfigDict(from_attributes=True)  # Sử dụng ConfigDict


class GiaoVienBase(BaseModel):
    id_gv: int
    ten_gv: str
    gioitinh_gv: str
    ngaysinh_gv: date
    diachi_gv: str
    sdt_gv: str
    email_gv: str
    tai_khoan_quyen: Optional[int] = None  # Quyền từ tài khoản
    id_taikhoan: Optional[int] = None  # ID tài khoản
    id_lh: Optional[int]  # Có thể không có lớp học
    lop_hoc_ten: Optional[str] = None  # Tên lớp học

    model_config = ConfigDict(from_attributes=True)


class LopHocBase(BaseModel):
    id_lh: int
    lophoc: str
    giao_vien: List[GiaoVienBase] = None  # Giáo viên dạy lớp học
    nam_hoc: Optional[NamHocBase] = None  # Năm học
    tong_so_hoc_sinh: Optional[int] = None  # Tổng số học sinh trong lớp

    model_config = ConfigDict(from_attributes=True)


class PhuHuynh_HocSinh(BaseModel):
    id_ph: Optional[int] = None
    ten_ph: Optional[str] = None
    gioitinh_ph: Optional[str] = None
    ngaysinh_ph: Optional[date] = None
    sdt_ph: Optional[str] = None
    diachi_ph: Optional[str] = None
    quanhe: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PhuHuynhImages(BaseModel):
    id_image: int
    id_ph: int
    image_path: str

    model_config = ConfigDict(from_attributes=True)


class PhuHuynhFullResponse(BaseModel):
    id_ph: Optional[int] = None
    ten_ph: Optional[str] = None
    gioitinh_ph: Optional[str] = None
    ngaysinh_ph: Optional[date] = None
    sdt_ph: Optional[str] = None
    diachi_ph: Optional[str] = None
    quanhe: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TeacherImageResponse(BaseModel):
    id_gv: int
    image_path: str

    model_config = ConfigDict(from_attributes=True)


class StudentImageResponse(BaseModel):
    id_hs: int
    image_path: str

    model_config = ConfigDict(from_attributes=True)


class PhuHuynhImageCreate(BaseModel):
    id_ph: int
    image_path: str


class FrameData(BaseModel):
    frame: str


class PhuHuynhImageResponse(BaseModel):
    id_image: int
    id_ph: int
    image_path: str
    vector: List[float] = None

    model_config = ConfigDict(from_attributes=True)


class PhuHuynhFullUpdate(BaseModel):
    ten_ph: Optional[str] = None
    gioitinh_ph: Optional[str] = None
    ngaysinh_ph: Optional[date] = None
    sdt_ph: Optional[str] = None
    diachi_ph: Optional[str] = None
    quanhe: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PhuHuynhUpdate(BaseModel):
    id_ph: int
    ten_ph: Optional[str] = None
    gioitinh_ph: Optional[str] = None
    ngaysinh_ph: Optional[date] = None
    sdt_ph: Optional[str] = None
    diachi_ph: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PhuHuynhHocSinhResponse(PhuHuynh_HocSinh):
    pass


class GiaoVienCreate(BaseModel):
    ten_gv: str
    gioitinh_gv: str
    ngaysinh_gv: date
    sdt_gv: str
    diachi_gv: str
    email_gv: str
    taikhoan: str  # Tài khoản
    matkhau: str  # Mật khẩu
    quyen: int  # Quyền

    model_config = ConfigDict(from_attributes=True)


class BestMatch(BaseModel):
    id_ph: int
    image_path: str
    distance: float


class RecognitionResult(BaseModel):
    success: bool
    message: str
    data: Optional[BestMatch]


class GiaoVienUpdate(BaseModel):
    id_gv: int
    ten_gv: Optional[str] = None
    gioitinh_gv: Optional[str] = None
    ngaysinh_gv: Optional[date] = None
    diachi_gv: Optional[str] = None
    sdt_gv: Optional[str] = None
    email_gv: Optional[str] = None
    quyen: Optional[int] = None  # Cập nhật quyền
    id_lh: Optional[int]  # Thêm trường id_lh vào đây

    model_config = ConfigDict(from_attributes=True)


class GiaoVienResponse(GiaoVienBase):
    pass


class GiaoVienCreateResponse(BaseModel):
    id_gv: int
    ten_gv: str
    gioitinh_gv: str
    ngaysinh_gv: date
    diachi_gv: str
    sdt_gv: str
    email_gv: str
    id_taikhoan: int
    quyen: int
    id_lh: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class PhuHuynhInfo(BaseModel):
    id_ph: Optional[int] = None
    ten_ph: str
    quanhe: str
    gioitinh_ph: str


class HocSinhBase(BaseModel):
    id_hs: int
    ten_hs: str
    gioitinh_hs: str
    ngaysinh_hs: date
    lop_hoc_ten: Optional[str] = None
    nam_hoc: Optional[str] = None
    phu_huynh: Optional[List[PhuHuynhInfo]] = None
    id_taikhoan: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class HocSinhCreate(BaseModel):
    ten_hs: str
    gioitinh_hs: str
    ngaysinh_hs: date
    taikhoan: str
    matkhau: str
    quyen: int = 2  # Mặc định quyền học sinh
    phu_huynh: Optional[List[PhuHuynhInfo]] = None

    model_config = ConfigDict(from_attributes=True)


class HocSinhResponse(HocSinhBase):
    pass


class LopHocCreate(BaseModel):
    lophoc: str
    id_nh: int  # ID năm học
    id_gv: List[int] = None  # ID giáo viên

    model_config = ConfigDict(from_attributes=True)


class LopHocUpdate(BaseModel):
    id_lh: int  # ID lớp học, cần thiết để cập nhật
    lophoc: Optional[str] = None
    id_nh: Optional[int] = None
    id_gv: Optional[List[int]] = None  # Danh sách ID giáo viên

    model_config = ConfigDict(from_attributes=True)


class LopHocResponse(LopHocBase):
    pass


class PhuHuynhCreate(BaseModel):
    ten_ph: str
    gioitinh_ph: str
    ngaysinh_ph: date
    sdt_ph: str
    diachi_ph: str

    model_config = ConfigDict(from_attributes=True)


class PhuHuynhUpdate(BaseModel):
    id_ph: Optional[int] = None  # Trường này vẫn giữ để có thể cập nhật
    ten_ph: Optional[str] = None
    gioitinh_ph: Optional[str] = None
    ngaysinh_ph: Optional[date] = None
    sdt_ph: Optional[str] = None
    diachi_ph: Optional[str] = None
    quanhe: Optional[str] = None  # Thêm trường quan hệ

    model_config = ConfigDict(from_attributes=True)


class HocSinhUpdate(BaseModel):
    ten_hs: Optional[str] = None
    gioitinh_hs: Optional[str] = None
    ngaysinh_hs: Optional[date] = None
    lop_hoc_ten: Optional[str] = None
    phu_huynh: Optional[List[PhuHuynhUpdate]] = []  # Thay đổi đây để có thể thêm phụ huynh

    model_config = ConfigDict(from_attributes=True)


class PhuHuynhResponse(PhuHuynhBase):
    pass


class TaiKhoanCreate(BaseModel):
    taikhoan: str
    matkhau: str
    quyen: int

    model_config = ConfigDict(from_attributes=True)


class TaiKhoanUpdate(BaseModel):
    taikhoan: Optional[str] = None
    matkhau: Optional[str] = None
    quyen: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class TaiKhoanResponse(TaiKhoanBase):
    pass


class NamHocCreate(BaseModel):
    namhoc: str  # Cần có trường này để tạo mới

    model_config = ConfigDict(from_attributes=True)


class NamHocUpdate(BaseModel):
    namhoc: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class NamHocResponse(NamHocBase):
    id_nh: int

    model_config = ConfigDict(from_attributes=True)


class DiemDanhCreate(BaseModel):
    id_hs: int
    id_lh: int
    ngay: date
    gio_vao: time


class DiemDanhResponse(BaseModel):
    id: int
    id_hs: int
    id_lh: int
    ngay: date
    gio_vao: time
    gio_ra: Optional[time] = None
    id_ph_don: Optional[int] = None


class DiemDanhResponseWithMessage(BaseModel):
    message: str
    data: DiemDanhResponse


class DiemDanhDetail(BaseModel):
    ho_ten_hoc_sinh: str
    gio_vao: Optional[str]
    gio_ra: Optional[str]
    ten_phu_huynh: str
    quan_he: str

    model_config = ConfigDict(from_attributes=True)


class DiemDanhResponseList(BaseModel):
    data: List[DiemDanhDetail]


GiaoVienBase.update_forward_refs()
LopHocBase.update_forward_refs()
TaiKhoanBase.update_forward_refs()
PhuHuynhBase.update_forward_refs()
NamHocBase.update_forward_refs()
