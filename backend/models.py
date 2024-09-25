from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from config import settings

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
    email_gv = Column(String(20), nullable=False)
    id_taikhoan = Column(Integer, ForeignKey('TaiKhoan.id_taikhoan'), nullable=False)

    tai_khoan = relationship("TaiKhoan", back_populates="giao_vien")
    lop_hocs = relationship("LopHoc", back_populates="giao_vien")


# Mô hình HocSinh
class HocSinh(Base):
    __tablename__ = 'HocSinh'

    id_hs = Column(Integer, primary_key=True, index=True)
    ten_hs = Column(String(100), nullable=False)
    gioitinh_hs = Column(String(10), nullable=False)
    ngaysinh_hs = Column(Date, nullable=False)
    id_lh = Column(Integer, ForeignKey('LopHoc.id_lh'))
    id_taikhoan = Column(Integer, ForeignKey('TaiKhoan.id_taikhoan'))

    # Relationship with LopHoc table
    lop_hoc = relationship("LopHoc", back_populates="hoc_sinh")

    # Relationship with TaiKhoan table
    tai_khoan = relationship("TaiKhoan", back_populates="hoc_sinh")

    # Relationship with PhuHuynh_HocSinh table
    phu_huynhs = relationship("PhuHuynh_HocSinh", back_populates="hoc_sinh")


# Mô hình NamHoc
class NamHoc(Base):
    __tablename__ = 'NamHoc'

    id_nh = Column(Integer, primary_key=True, index=True)
    namhoc = Column(String(9), nullable=False)

    # Quan hệ với bảng LopHoc
    lop_hocs = relationship("LopHoc", back_populates="nam_hoc")


# Mô hình LopHoc
class LopHoc(Base):
    __tablename__ = 'LopHoc'

    id_lh = Column(Integer, primary_key=True, index=True)
    lophoc = Column(String(80), nullable=False)
    id_gv = Column(Integer, ForeignKey('GiaoVien.id_gv'))
    id_nh = Column(Integer, ForeignKey('NamHoc.id_nh'))

    giao_vien = relationship("GiaoVien", back_populates="lop_hocs")
    nam_hoc = relationship("NamHoc", back_populates="lop_hocs")
    hoc_sinh = relationship("HocSinh", back_populates="lop_hoc")


# Mô hình PhuHuynh
class PhuHuynh(Base):
    __tablename__ = 'PhuHuynh'

    id_ph = Column(Integer, primary_key=True, index=True)
    ten_ph = Column(String(100), nullable=False)
    gioitinh_ph = Column(String(5), nullable=False)
    ngaysinh_ph = Column(Date, nullable=False)
    sdt_ph = Column(String(20), nullable=False)
    diachi_ph = Column(String(255), nullable=False)

    # Quan hệ với bảng PhuHuynh_HocSinh
    phu_hoc_sinh = relationship("PhuHuynh_HocSinh", back_populates="phu_huynh")

    # Quan hệ với bảng PhuHuynh_Images
    images = relationship("PhuHuynh_Images", back_populates="phu_huynh")


# Mô hình PhuHuynh_HocSinh
class PhuHuynh_HocSinh(Base):
    __tablename__ = 'PhuHuynh_HocSinh'

    id_ph = Column(Integer, ForeignKey('PhuHuynh.id_ph'), primary_key=True)
    id_hs = Column(Integer, ForeignKey('HocSinh.id_hs'), primary_key=True)
    quanhe = Column(String(20), nullable=False)

    # Quan hệ với bảng PhuHuynh
    phu_huynh = relationship("PhuHuynh", back_populates="phu_hoc_sinh")

    # Quan hệ với bảng HocSinh
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

    # Relationship with HocSinh table
    hoc_sinh = relationship("HocSinh", back_populates="tai_khoan", uselist=False)


# Mô hình PhuHuynh_Images
class PhuHuynh_Images(Base):
    __tablename__ = 'PhuHuynh_Images'

    id_image = Column(Integer, primary_key=True, index=True)
    id_ph = Column(Integer, ForeignKey('PhuHuynh.id_ph'))
    image_path = Column(String(255), nullable=False)

    # Quan hệ với bảng PhuHuynh
    phu_huynh = relationship("PhuHuynh", back_populates="images")
