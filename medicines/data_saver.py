from database import DatabaseConnection
import logging
from typing import Dict

# ตั้งค่า logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataSaver:
    def __init__(self):
        self.db = DatabaseConnection()
    
    def save_medicine_data(self, medicine_info: Dict) -> bool:
        """บันทึกข้อมูลยาทั้งหมดลงตารางเดียว - ลบ medicine_purpose แล้ว"""
        if not self.db.connect():
            return False
        
        try:
            # บันทึกข้อมูลยาในตารางเดียว (ลบ medicine_purpose)
            query = """
            INSERT INTO medicines (
                medicine_name, medicine_category,
                section_1_1_name, section_1_2_purpose,
                section_2_1_contraindications, section_2_2_warnings,
                section_3_1_dosage, section_3_2_missed_dose, section_3_3_overdose,
                section_4_precautions,
                section_5_1_severe_effects, section_5_2_mild_effects,
                section_6_storage,
                section_7_appearance_ingredients
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) RETURNING id
            """
            
            self.db.cursor.execute(query, (
                medicine_info.get('name', ''),
                medicine_info.get('category', ''),
                medicine_info.get('section_1_1_name', ''),
                medicine_info.get('section_1_2_purpose', ''),
                medicine_info.get('section_2_1_contraindications', ''),
                medicine_info.get('section_2_2_warnings', ''),
                medicine_info.get('section_3_1_dosage', ''),
                medicine_info.get('section_3_2_missed_dose', ''),
                medicine_info.get('section_3_3_overdose', ''),
                medicine_info.get('section_4_precautions', ''),
                medicine_info.get('section_5_1_severe_effects', ''),
                medicine_info.get('section_5_2_mild_effects', ''),
                medicine_info.get('section_6_storage', ''),
                medicine_info.get('section_7_appearance_ingredients', '')
            ))
            
            result = self.db.cursor.fetchone()
            self.db.connection.commit()
            
            if result:
                medicine_id = result['id']
                logger.info(f"✅ บันทึกข้อมูลยาสำเร็จ ID: {medicine_id}")
                
                # แสดงสรุปข้อมูลที่บันทึก
                print(f"\n🎉 บันทึกข้อมูลลงฐานข้อมูลสำเร็จ!")
                print(f"📊 รายละเอียด:")
                print(f"   🆔 ID: {medicine_id}")
                print(f"   🏷️ ชื่อยา: {medicine_info.get('name', 'ไม่ระบุ')}")
                print(f"   📂 หมวดหมู่: {medicine_info.get('category', 'ไม่ระบุ')}")
                
                # นับจำนวนส่วนที่มีข้อมูล
                sections_with_data = 0
                total_sections = 12
                
                section_mapping = {
                    'section_1_1_name': '1.1 ชื่อยา',
                    'section_1_2_purpose': '1.2 จุดประสงค์',
                    'section_2_1_contraindications': '2.1 ข้อห้าม',
                    'section_2_2_warnings': '2.2 ข้อควรระวัง',
                    'section_3_1_dosage': '3.1 วิธีใช้',
                    'section_3_2_missed_dose': '3.2 ลืมกินยา',
                    'section_3_3_overdose': '3.3 กินยาเกิน',
                    'section_4_precautions': '4. ข้อควรปฏิบัติ',
                    'section_5_1_severe_effects': '5.1 อาการรุนแรง',
                    'section_5_2_mild_effects': '5.2 อาการไม่รุนแรง',
                    'section_6_storage': '6. วิธีเก็บยา',
                    'section_7_appearance_ingredients': '7. ลักษณะและส่วนประกอบ'
                }
                
                print(f"   📋 ข้อมูลแต่ละส่วน:")
                for section_key, section_name in section_mapping.items():
                    has_data = bool(medicine_info.get(section_key, '').strip())
                    status = "✅" if has_data else "❌"
                    print(f"      {status} {section_name}")
                    if has_data:
                        sections_with_data += 1
                
                print(f"   📊 สรุป: {sections_with_data}/{total_sections} ส่วนมีข้อมูล")
                
                return True
            else:
                logger.error("ไม่สามารถรับ ID ของข้อมูลที่บันทึก")
                return False
                
        except Exception as e:
            logger.error(f"เกิดข้อผิดพลาดในการบันทึกข้อมูล: {e}")
            self.db.connection.rollback()
            return False
        finally:
            self.db.disconnect()
    
    def get_medicine_by_id(self, medicine_id: int) -> Dict:
        """ดึงข้อมูลยาตาม ID"""
        if not self.db.connect():
            return {}
        
        try:
            query = "SELECT * FROM medicines WHERE id = %s"
            result = self.db.fetch_one(query, (medicine_id,))
            return dict(result) if result else {}
        except Exception as e:
            logger.error(f"ไม่สามารถดึงข้อมูลยา: {e}")
            return {}
        finally:
            self.db.disconnect()
    
    def get_all_medicines(self) -> list:
        """ดึงข้อมูลยาทั้งหมด"""
        if not self.db.connect():
            return []
        
        try:
            query = "SELECT id, medicine_name, medicine_category, created_at FROM medicines ORDER BY created_at DESC"
            results = self.db.fetch_all(query)
            return results if results else []
        except Exception as e:
            logger.error(f"ไม่สามารถดึงข้อมูลยาทั้งหมด: {e}")
            return []
        finally:
            self.db.disconnect()
    
    def search_medicines(self, search_term: str) -> list:
        """ค้นหายาตามชื่อ"""
        if not self.db.connect():
            return []
        
        try:
            query = """
            SELECT id, medicine_name, medicine_category, created_at 
            FROM medicines 
            WHERE medicine_name ILIKE %s OR medicine_category ILIKE %s
            ORDER BY created_at DESC
            """
            search_pattern = f"%{search_term}%"
            results = self.db.fetch_all(query, (search_pattern, search_pattern))
            return results if results else []
        except Exception as e:
            logger.error(f"ไม่สามารถค้นหายา: {e}")
            return []
        finally:
            self.db.disconnect()