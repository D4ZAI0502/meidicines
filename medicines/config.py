import os
from dotenv import load_dotenv

# โหลดตัวแปรจากไฟล์ .env
load_dotenv()

# การตั้งค่าฐานข้อมูล PostgreSQL
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'medicine_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '0502'),
    'port': os.getenv('DB_PORT', '5432')
}

# การตั้งค่าอื่นๆ
PDF_FOLDER = os.getenv('PDF_FOLDER', './pdf_files/')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')