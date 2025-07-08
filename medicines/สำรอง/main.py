#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
from pathlib import Path
import json

# Import modules
from pdf_extractor import PDFExtractor
from data_saver import DataSaver
from config import PDF_FOLDER

# ตั้งค่า logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('medicine_extraction.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def process_single_pdf(pdf_path: str) -> bool:
    """ประมวลผลไฟล์ PDF เดียว"""
    logger.info(f"เริ่มประมวลผลไฟล์: {pdf_path}")
    
    # สร้าง objects
    extractor = PDFExtractor()
    saver = DataSaver()
    
    try:
        # แปลงข้อมูลจาก PDF
        medicine_info = extractor.process_pdf(pdf_path)
        
        if not medicine_info:
            logger.error(f"ไม่สามารถแปลงข้อมูลจาก PDF: {pdf_path}")
            return False
        
        # ข้อมูลจะแสดงแล้วในฟังก์ชัน extract_medicine_info
        print("\n" + "="*60)
        print("📋 สรุปข้อมูลที่แยกได้:")
        print(f"🏷️  ชื่อยา: {medicine_info.get('name', 'ไม่พบ')}")
        print(f"📂 หมวดหมู่: {medicine_info.get('category', 'ไม่พบ')}")
        
        # นับจำนวนส่วนที่มีข้อมูล
        sections_with_data = 0
        section_keys = [
            'section_1_1_name', 'section_1_2_purpose', 'section_2_1_contraindications',
            'section_2_2_warnings', 'section_3_1_dosage', 'section_3_2_missed_dose',
            'section_3_3_overdose', 'section_4_precautions', 'section_5_1_severe_effects',
            'section_5_2_mild_effects', 'section_6_storage', 'section_7_appearance_ingredients'
        ]
        
        for key in section_keys:
            if medicine_info.get(key, '').strip():
                sections_with_data += 1
        
        print(f"📋 ข้อมูลที่พบ: {sections_with_data}/12 ส่วน")
        print("="*60)
        
        # บันทึกเป็น JSON (สำหรับตรวจสอบ)
        json_filename = f"{Path(pdf_path).stem}_extracted.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(medicine_info, f, ensure_ascii=False, indent=2)
        logger.info(f"บันทึกไฟล์ JSON: {json_filename}")
        
        # บันทึกลงฐานข้อมูล
        if saver.save_medicine_data(medicine_info):
            logger.info(f"บันทึกข้อมูลลงฐานข้อมูลสำเร็จ: {pdf_path}")
            return True
        else:
            logger.error(f"ไม่สามารถบันทึกข้อมูลลงฐานข้อมูล: {pdf_path}")
            return False
            
    except Exception as e:
        logger.error(f"เกิดข้อผิดพลาดขณะประมวลผล {pdf_path}: {e}")
        return False

def process_multiple_pdfs(folder_path: str) -> None:
    """ประมวลผลไฟล์ PDF หลายไฟล์ในโฟลเดอร์"""
    logger.info(f"เริ่มประมวลผลไฟล์ PDF ในโฟลเดอร์: {folder_path}")
    
    if not os.path.exists(folder_path):
        logger.error(f"ไม่พบโฟลเดอร์: {folder_path}")
        return
    
    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        logger.warning(f"ไม่พบไฟล์ PDF ในโฟลเดอร์: {folder_path}")
        return
    
    logger.info(f"พบไฟล์ PDF จำนวน {len(pdf_files)} ไฟล์")
    
    success_count = 0
    fail_count = 0
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(folder_path, pdf_file)
        if process_single_pdf(pdf_path):
            success_count += 1
        else:
            fail_count += 1
    
    logger.info(f"สรุปผลการประมวลผล: สำเร็จ {success_count} ไฟล์, ล้มเหลว {fail_count} ไฟล์")

def main():
    """ฟังก์ชันหลัก"""
    print("=" * 60)
    print("ระบบแปลงข้อมูลยาจาก PDF ไปยัง PostgreSQL")
    print("=" * 60)
    
    while True:
        print("\nเลือกตัวเลือก:")
        print("1. ประมวลผลไฟล์ PDF เดียว")
        print("2. ประมวลผลไฟล์ PDF ทั้งหมดในโฟลเดอร์")
        print("3. ตรวจสอบการเชื่อมต่อฐานข้อมูล")
        print("4. ออกจากโปรแกรม")
        
        choice = input("\nกรุณาเลือก (1-4): ").strip()
        
        if choice == '1':
            pdf_path = input("กรุณาใส่ path ของไฟล์ PDF: ").strip()
            if os.path.exists(pdf_path):
                process_single_pdf(pdf_path)
            else:
                print(f"ไม่พบไฟล์: {pdf_path}")
        
        elif choice == '2':
            folder_path = input(f"กรุณาใส่ path ของโฟลเดอร์ (หรือกด Enter เพื่อใช้ {PDF_FOLDER}): ").strip()
            if not folder_path:
                folder_path = PDF_FOLDER
            process_multiple_pdfs(folder_path)
        
        elif choice == '3':
            from database import DatabaseConnection
            db = DatabaseConnection()
            if db.connect():
                print("✅ เชื่อมต่อฐานข้อมูลสำเร็จ")
                db.disconnect()
            else:
                print("❌ ไม่สามารถเชื่อมต่อฐานข้อมูลได้")
        
        elif choice == '4':
            print("ขอบคุณที่ใช้ระบบ!")
            sys.exit(0)
        
        else:
            print("กรุณาเลือกตัวเลือกที่ถูกต้อง (1-4)")

if __name__ == "__main__":
    main()