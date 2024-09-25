from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from config import settings

# Tạo engine để kết nối với cơ sở dữ liệu
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class TaiKhoan(Base):
    __tablename__ = "TaiKhoan"
    id_taikhoan = Column(Integer, primary_key=True, index=True, autoincrement=True)
    taikhoan = Column(String(50), unique=True, index=True)
    matkhau = Column(String(255))
    quyen = Column(Integer)
    id_gv = Column(Integer, ForeignKey('GiaoVien.id_gv'), nullable=True)
    id_hs = Column(Integer, ForeignKey('HocSinh.id_hs'), nullable=True)

    # Relationships
    giao_vien = relationship("GiaoVien", back_populates="tai_khoan", uselist=False)
    hoc_sinh = relationship("HocSinh", back_populates="tai_khoan", uselist=False)


class GiaoVien(Base):
    __tablename__ = "GiaoVien"
    id_gv = Column(Integer, primary_key=True, index=True)
    ten_gv = Column(String(100), nullable=False)
    gioitinh_gv = Column(String(5), nullable=False)
    ngaysinh_gv = Column(Date, nullable=False)
    diachi_gv = Column(String(200), nullable=False)
    sdt_gv = Column(String(20), nullable=False)

    # Relationships
    tai_khoan = relationship("TaiKhoan", back_populates="giao_vien", uselist=False)
    lop_hoc = relationship("LopHoc_GiaoVien", back_populates="giao_vien")


class HocSinh(Base):
    __tablename__ = "HocSinh"
    id_hs = Column(Integer, primary_key=True, index=True)
    ten_hs = Column(String(100), nullable=False)
    gioitinh_hs = Column(String(5), nullable=False)
    ngaysinh_hs = Column(Date, nullable=False)

    # Relationships
    tai_khoan = relationship("TaiKhoan", back_populates="hoc_sinh", uselist=False)
    phu_huynh_hs = relationship("PhuHuynh_HocSinh", back_populates="hoc_sinh")
    lop_hoc_hs = relationship("LopHoc_HocSinh", back_populates="hoc_sinh")


class LopHoc(Base):
    __tablename__ = "LopHoc"
    id_lh = Column(Integer, primary_key=True, index=True)
    lophoc = Column(String(80), nullable=False)
    id_nh = Column(Integer, ForeignKey('NamHoc.id_nh'))

    # Relationships
    giao_vien_lop = relationship("LopHoc_GiaoVien", back_populates="lop_hoc")
    hoc_sinh_lop = relationship("LopHoc_HocSinh", back_populates="lop_hoc")
    nam_hoc_ref = relationship("NamHoc", back_populates="lop_hoc")


class NamHoc(Base):
    __tablename__ = "NamHoc"

    id_nh = Column(Integer, primary_key=True, index=True)
    namhoc = Column(String, index=True, unique=True)

    # Relationships
    lop_hoc = relationship("LopHoc", back_populates="nam_hoc_ref")


class LopHoc_GiaoVien(Base):
    __tablename__ = "LopHoc_GiaoVien"
    id_lh = Column(Integer, ForeignKey('LopHoc.id_lh'), primary_key=True)
    id_gv = Column(Integer, ForeignKey('GiaoVien.id_gv'), primary_key=True)

    # Relationships
    lop_hoc = relationship("LopHoc", back_populates="giao_vien_lop")
    giao_vien = relationship("GiaoVien", back_populates="lop_hoc")


class LopHoc_HocSinh(Base):
    __tablename__ = "LopHoc_HocSinh"
    id_lh = Column(Integer, ForeignKey('LopHoc.id_lh'), primary_key=True)
    id_hs = Column(Integer, ForeignKey('HocSinh.id_hs'), primary_key=True)

    # Relationships
    lop_hoc = relationship("LopHoc", back_populates="hoc_sinh_lop")
    hoc_sinh = relationship("HocSinh", back_populates="lop_hoc_hs")


class PhuHuynh(Base):
    __tablename__ = "PhuHuynh"
    id_ph = Column(Integer, primary_key=True, index=True)
    ten_ph = Column(String(100), nullable=False)
    gioitinh_ph = Column(String(5), nullable=False)
    ngaysinh_ph = Column(Date, nullable=False)
    sdt_ph = Column(String(20), nullable=False)
    diachi_ph = Column(String(255), nullable=False)

    # Relationships
    phu_huynh_hs = relationship("PhuHuynh_HocSinh", back_populates="phu_huynh")
    phu_huynh_images = relationship("PhuHuynh_Images", back_populates="phu_huynh")
    phu_huynh_vectors = relationship("PhuHuynh_Vector", back_populates="phu_huynh")


class PhuHuynh_HocSinh(Base):
    __tablename__ = "PhuHuynh_HocSinh"
    id_ph = Column(Integer, ForeignKey('PhuHuynh.id_ph'), primary_key=True)
    id_hs = Column(Integer, ForeignKey('HocSinh.id_hs'), primary_key=True)
    quanhe = Column(String(20), nullable=False)

    # Relationships
    phu_huynh = relationship("PhuHuynh", back_populates="phu_huynh_hs")
    hoc_sinh = relationship("HocSinh", back_populates="phu_huynh_hs")


class PhuHuynh_Vector(Base):
    __tablename__ = "PhuHuynh_Vector"
    id_mapping = Column(Integer, primary_key=True, index=True)
    id_ph = Column(Integer, ForeignKey('PhuHuynh.id_ph'))
    id_index = Column(Integer, nullable=False)

    # Relationships
    phu_huynh = relationship("PhuHuynh", back_populates="phu_huynh_vectors")


class PhuHuynh_Images(Base):
    __tablename__ = "PhuHuynh_Images"
    id_image = Column(Integer, primary_key=True, index=True)
    id_ph = Column(Integer, ForeignKey('PhuHuynh.id_ph'))
    image_path = Column(String(255), nullable=False)

    # Relationships
    phu_huynh = relationship("PhuHuynh", back_populates="phu_huynh_images")