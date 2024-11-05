from sqlalchemy import create_engine, text
from config import settings

# Tạo engine kết nối đến cơ sở dữ liệu
engine = create_engine(settings.DATABASE_URL)

# Kết nối và thử truy vấn cơ sở dữ liệu
with engine.connect() as connection:
    result = connection.execute(text("SELECT 1"))
    print("Database connection successful!")
    for row in result:
        print(row)
