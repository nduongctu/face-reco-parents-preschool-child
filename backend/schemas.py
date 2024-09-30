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
    id_taikhoan: Optional[int] = None

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
    sdt_gv: str
    diachi_gv: str
    email_gv: str
    taikhoan: str
    matkhau: str
    quyen: int

    model_config = ConfigDict(from_attributes=True)


class GiaoVienUpdate(BaseModel):
    id_gv: int
    ten_gv: Optional[str] = None
    gioitinh_gv: Optional[str] = None
    ngaysinh_gv: Optional[date] = None
    diachi_gv: Optional[str] = None
    sdt_gv: Optional[str] = None
    email_gv: Optional[str] = None
    quyen: Optional[int] = None
    lop_hoc_ten: Optional[List[str]] = None

    model_config = ConfigDict(from_attributes=True)


class GiaoVienResponse(GiaoVienBase):
    pass


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
    ten_gv: Optional[str] = None
    namhoc: str

    model_config = ConfigDict(from_attributes=True)


class LopHocUpdate(BaseModel):
    lophoc: Optional[str] = None
    ten_gv: Optional[str] = None
    namhoc: Optional[str] = None

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
    lop_hoc_ten: Optional[str]
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
    namhoc: str

    model_config = ConfigDict(from_attributes=True)


class NamHocUpdate(BaseModel):
    namhoc: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class NamHocResponse(NamHocBase):
    pass


# Cập nhật các forward references cho các mô hình Pydantic
GiaoVienBase.update_forward_refs()
LopHocBase.update_forward_refs()
TaiKhoanBase.update_forward_refs()
PhuHuynhBase.update_forward_refs()
NamHocBase.update_forward_refs()
