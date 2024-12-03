from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date, JSON, Time, Text
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from config import settings
import numpy as np
import json
# Tạo engine để kết nối với cơ sở dữ liệu
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Mô hình GiaoVien
class GiaoVien(Base):
    __tablename__ = 'GiaoVien'

    id_gv = Column(Integer, primary_key=True, index=True)
    ten_gv = Column(String(100), nullable=False)
    gioitinh_gv = Column(String(5), nullable=False)
    ngaysinh_gv = Column(Date, nullable=False)
    diachi_gv = Column(String(200), nullable=False)
    sdt_gv = Column(String(20), nullable=False)
    email_gv = Column(String(100), nullable=False)
    id_taikhoan = Column(Integer, ForeignKey('TaiKhoan.id_taikhoan'), nullable=False)
    id_lh = Column(Integer, ForeignKey('LopHoc.id_lh'))

    tai_khoan = relationship("TaiKhoan", back_populates="giao_vien")
    lop_hoc = relationship("LopHoc", back_populates="giao_viens")
    images = relationship("GiaoVienImages", back_populates="teacher")


# Mô hình HocSinh
class HocSinh(Base):
    __tablename__ = 'HocSinh'

    id_hs = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ten_hs = Column(String(100), nullable=False)
    gioitinh_hs = Column(String(10), nullable=False)
    ngaysinh_hs = Column(Date, nullable=False)
    id_lh = Column(Integer, ForeignKey('LopHoc.id_lh'))
    id_taikhoan = Column(Integer, ForeignKey('TaiKhoan.id_taikhoan'))

    lop_hoc = relationship("LopHoc", back_populates="hoc_sinhs")
    tai_khoan = relationship("TaiKhoan", back_populates="hoc_sinh")
    phu_huynhs = relationship("PhuHuynh_HocSinh", back_populates="hoc_sinh")
    images = relationship("HocSinhImages", back_populates="hoc_sinh")
    diem_danhs = relationship("DiemDanh", back_populates="hoc_sinh")


# Mô hình NamHoc
class NamHoc(Base):
    __tablename__ = 'NamHoc'

    id_nh = Column(Integer, primary_key=True, index=True)
    namhoc = Column(String(9), nullable=False)

    lop_hocs = relationship("LopHoc", back_populates="nam_hoc")


# Mô hình LopHoc
class LopHoc(Base):
    __tablename__ = 'LopHoc'

    id_lh = Column(Integer, primary_key=True, index=True)
    lophoc = Column(String(80), nullable=False)
    id_nh = Column(Integer, ForeignKey('NamHoc.id_nh'))

    giao_viens = relationship("GiaoVien", back_populates="lop_hoc")  # Một lớp có nhiều giáo viên
    hoc_sinhs = relationship("HocSinh", back_populates="lop_hoc")  # Một lớp có nhiều học sinh
    nam_hoc = relationship("NamHoc", back_populates="lop_hocs")
    lop_diem_danhs = relationship("DiemDanh", back_populates="lop_hoc")


# Mô hình PhuHuynh
class PhuHuynh(Base):
    __tablename__ = 'PhuHuynh'

    id_ph = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ten_ph = Column(String(100), nullable=False)
    gioitinh_ph = Column(String(5), nullable=False)
    ngaysinh_ph = Column(Date, nullable=True)
    sdt_ph = Column(String(20), nullable=True)
    diachi_ph = Column(String(255), nullable=True)

    phu_hoc_sinh = relationship("PhuHuynh_HocSinh", back_populates="phu_huynh")
    images = relationship("PhuHuynh_Images", back_populates="phu_huynh")
    diem_danh_don = relationship("DiemDanh", back_populates="phu_huynh_don")


# Mô hình PhuHuynh_HocSinh
class PhuHuynh_HocSinh(Base):
    __tablename__ = 'PhuHuynh_HocSinh'

    id_ph = Column(Integer, ForeignKey('PhuHuynh.id_ph'), primary_key=True, nullable=False)
    id_hs = Column(Integer, ForeignKey('HocSinh.id_hs'), primary_key=True, nullable=False)
    quanhe = Column(String(20), nullable=False)

    phu_huynh = relationship("PhuHuynh", back_populates="phu_hoc_sinh")
    hoc_sinh = relationship("HocSinh", back_populates="phu_huynhs")


# Mô hình TaiKhoan
class TaiKhoan(Base):
    __tablename__ = 'TaiKhoan'

    id_taikhoan = Column(Integer, primary_key=True, index=True)
    taikhoan = Column(String(50), nullable=False)
    matkhau = Column(String(255), nullable=False)
    quyen = Column(Integer, nullable=False)

    # Relationship with GiaoVien table
    giao_vien = relationship("GiaoVien", back_populates="tai_khoan", uselist=False)
    hoc_sinh = relationship("HocSinh", back_populates="tai_khoan", uselist=False)


# Mô hình PhuHuynh_Images
class PhuHuynh_Images(Base):
    __tablename__ = 'PhuHuynh_Images'

    id_image = Column(Integer, primary_key=True, index=True)
    id_ph = Column(Integer, ForeignKey('PhuHuynh.id_ph'))
    image_path = Column(String(255), nullable=False)
    vector = Column(Text, nullable=True)

    # Quan hệ với bảng PhuHuynh
    phu_huynh = relationship("PhuHuynh", back_populates="images")

    def get_embedding(self):
        if not self.vector:
            raise ValueError(f"Vector for image {self.id_image} is empty or None.")
        return np.array(json.loads(self.vector))  # Chuyển chuỗi JSON thành mảng numpy


# Mô hình GiaoVien_Images
class GiaoVienImages(Base):
    __tablename__ = 'GiaoVien_Images'

    id = Column(Integer, primary_key=True, autoincrement=True)  # Đảm bảo cột này tự động tăng
    id_gv = Column(Integer, ForeignKey('GiaoVien.id_gv'))  # Đảm bảo tên khóa ngoại chính xác
    image_path = Column(String, nullable=True)  # Đặt nullable=True nếu cần thiết

    # Quan hệ với bảng GiaoVien
    teacher = relationship("GiaoVien", back_populates="images")


# Mô hình HocSinh_Images
class HocSinhImages(Base):  # Đổi tên lớp cho phù hợp với quy ước PEP8
    __tablename__ = 'HocSinh_Images'

    id = Column(Integer, primary_key=True, index=True)
    id_hs = Column(Integer, ForeignKey('HocSinh.id_hs'))
    image_path = Column(String(255), nullable=False)

    # Quan hệ với bảng HocSinh
    hoc_sinh = relationship("HocSinh", back_populates="images")


class DiemDanh(Base):
    __tablename__ = 'DiemDanh'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_hs = Column(Integer, ForeignKey('HocSinh.id_hs'), nullable=False)
    id_lh = Column(Integer, ForeignKey('LopHoc.id_lh'), nullable=False)
    ngay = Column(Date, nullable=False)
    gio_vao = Column(Time, nullable=True)  # Chỉ lưu giờ vào, không cần nhận dạng
    gio_ra = Column(Time, nullable=True)  # Giờ ra về
    id_ph_don = Column(Integer, ForeignKey('PhuHuynh.id_ph'), nullable=True)  # ID phụ huynh đón (chỉ khi ra về)

    # Relationships
    hoc_sinh = relationship("HocSinh", back_populates="diem_danhs")
    lop_hoc = relationship("LopHoc", back_populates="lop_diem_danhs")
    phu_huynh_don = relationship("PhuHuynh", back_populates="diem_danh_don")
