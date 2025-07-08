import psycopg2
from psycopg2.extras import RealDictCursor
from config import DATABASE_CONFIG
import logging

# ตั้งค่า logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConnection:
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """เชื่อมต่อกับฐานข้อมูล PostgreSQL"""
        try:
            self.connection = psycopg2.connect(**DATABASE_CONFIG)
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            logger.info("เชื่อมต่อฐานข้อมูลสำเร็จ")
            return True
        except Exception as e:
            logger.error(f"เชื่อมต่อฐานข้อมูลไม่สำเร็จ: {e}")
            return False
    
    def disconnect(self):
        """ปิดการเชื่อมต่อฐานข้อมูล"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("ปิดการเชื่อมต่อฐานข้อมูลแล้ว")
    
    def execute_query(self, query, params=None):
        """ทำงานกับคำสั่ง SQL"""
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"ไม่สามารถทำงานกับคำสั่ง SQL: {e}")
            self.connection.rollback()
            return False
    
    def fetch_one(self, query, params=None):
        """ดึงข้อมูลหนึ่งแถว"""
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchone()
        except Exception as e:
            logger.error(f"ไม่สามารถดึงข้อมูล: {e}")
            return None
    
    def fetch_all(self, query, params=None):
        """ดึงข้อมูลทั้งหมด"""
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"ไม่สามารถดึงข้อมูล: {e}")
            return None
    
    def insert_medicine(self, medicine_data):
        """เพิ่มข้อมูลยาและส่งคืน ID - สำหรับตารางเดียว (ลบ medicine_purpose)"""
        query = """
        INSERT INTO medicines (medicine_name, medicine_category)
        VALUES (%s, %s) RETURNING id
        """
        try:
            self.cursor.execute(query, (
                medicine_data['name'],
                medicine_data['category']
            ))
            result = self.cursor.fetchone()
            self.connection.commit()
            return result['id']
        except Exception as e:
            logger.error(f"ไม่สามารถเพิ่มข้อมูลยา: {e}")
            self.connection.rollback()
            return None