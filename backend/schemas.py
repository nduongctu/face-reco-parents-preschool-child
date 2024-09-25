from pydantic import BaseModel, Field, conint, ConfigDict
from typing import Optional, List
from datetime import date


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
    tai_khoan_quyen: Optional[int] = None
    lop_hoc_ten: Optional[List[str]] = None

    model_config = ConfigDict(from_attributes=True)


class LopHocBase(BaseModel):
    id_lh: int
    lophoc: str
    giao_vien: Optional[GiaoVienBase] = None
    nam_hoc: Optional[NamHocBase] = None
    tong_so_hoc_sinh: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class GiaoVienCreate(BaseModel):
    ten_gv: str
    gioitinh_gv: str
    ngaysinh_gv: date
    diachi_gv: str
    sdt_gv: str
    taikhoan: str
    matkhau: str
    quyen: int = 1  # Mặc định quyền giáo viên
    lop_hoc_ten: Optional[List[str]] = None  # Danh sách tên lớp học


class GiaoVienUpdate(BaseModel):
    ten_gv: Optional[str] = None
    gioitinh_gv: Optional[str] = None
    ngaysinh_gv: Optional[date] = None
    diachi_gv: Optional[str] = None
    sdt_gv: Optional[str] = None
    quyen: Optional[conint(ge=0, le=1)] = None  # Quyền chỉ trong khoảng [0, 1]
    lop_hoc_ten: Optional[List[str]] = None


class GiaoVienResponse(GiaoVienBase):
    pass


class HocSinhBase(BaseModel):
    id_hs: int
    ten_hs: str
    gioitinh_hs: str
    ngaysinh_hs: date
    lop_hoc: Optional[LopHocBase] = None  # Sử dụng một lớp LopHoc duy nhất
    phu_huynh: Optional[List[PhuHuynhBase]] = None  # Danh sách phụ huynh
    tai_khoan: Optional[TaiKhoanBase] = None

    model_config = ConfigDict(from_attributes=True)  # Sử dụng ConfigDict


class HocSinhCreate(BaseModel):
    ten_hs: str
    gioitinh_hs: str
    ngaysinh_hs: date
    taikhoan: str
    matkhau: str
    quyen: int = 2  # Mặc định quyền học sinh
    lop_hoc_ids: List[int]  # Danh sách ID lớp học


class HocSinhUpdate(BaseModel):
    ten_hs: Optional[str] = None
    gioitinh_hs: Optional[str] = None
    ngaysinh_hs: Optional[date] = None
    lop_hoc_ids: Optional[List[int]] = []


class HocSinhResponse(HocSinhBase):
    pass


class LopHocCreate(BaseModel):
    lophoc: str
    ten_gv: Optional[str] = None
    namhoc: str


class LopHocUpdate(BaseModel):
    lophoc: Optional[str] = None
    ten_gv: Optional[str] = None
    namhoc: Optional[str] = None


class LopHocResponse(LopHocBase):
    pass


class PhuHuynhCreate(BaseModel):
    ten_ph: str
    gioitinh_ph: str
    ngaysinh_ph: date
    sdt_ph: str
    diachi_ph: str


class PhuHuynhUpdate(BaseModel):
    ten_ph: Optional[str] = None
    gioitinh_ph: Optional[str] = None
    ngaysinh_ph: Optional[date] = None
    sdt_ph: Optional[str] = None
    diachi_ph: Optional[str] = None


class PhuHuynhResponse(PhuHuynhBase):
    pass


class TaiKhoanCreate(BaseModel):
    taikhoan: str
    matkhau: str
    quyen: int


class TaiKhoanUpdate(BaseModel):
    taikhoan: Optional[str] = None
    matkhau: Optional[str] = None
    quyen: Optional[int] = None


class TaiKhoanResponse(TaiKhoanBase):
    pass


class NamHocCreate(BaseModel):
    namhoc: str


class NamHocUpdate(BaseModel):
    namhoc: Optional[str] = None


class NamHocResponse(NamHocBase):
    pass


# Cập nhật các forward references cho các mô hình Pydantic
GiaoVienBase.update_forward_refs()
LopHocBase.update_forward_refs()
TaiKhoanBase.update_forward_refs()
PhuHuynhBase.update_forward_refs()
NamHocBase.update_forward_refs()
