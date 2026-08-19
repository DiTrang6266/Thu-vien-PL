# -*- coding: utf-8 -*-
"""
Module: legal_parser.py
Mục đích: Bóc tách cấu trúc phân cấp (Chương -> Mục -> Điều -> Khoản -> Điểm)
của văn bản quy phạm pháp luật Việt Nam từ file PDF / DOCX / Text kèm số trang thực tế.
"""

import re
import os
from typing import Dict, List, Any, Optional
import fitz  # PyMuPDF


class LegalDocumentParser:
    """
    Trình phân tích cú pháp cấu trúc văn bản pháp luật Việt Nam.
    Bảo toàn nguyên vẹn ngữ cảnh phân cấp, số trang và câu chữ gốc.
    """

    # Regex nhận diện các cấp bậc pháp lý chuẩn Việt Nam
    RE_CHUONG = re.compile(r'^(CHƯƠNG|Chương)\s+([IVXLCDM\d]+)[\.\:\s]*(.*)$', re.IGNORECASE)
    RE_MUC = re.compile(r'^(MỤC|Mục)\s+(\d+)[\.\:\s]*(.*)$', re.IGNORECASE)
    RE_DIEU = re.compile(r'^(Điều|ĐIỀU)\s+(\d+)\.[\s\t]*(.*)$')
    RE_KHOAN = re.compile(r'^(\d+)\.\s+(.*)$')
    RE_DIEM = re.compile(r'^([a-zđ])\)\s+(.*)$', re.IGNORECASE)

    def __init__(self):
        pass

    def parse_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Đọc và phân tích file PDF văn bản pháp luật theo từng trang.
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Không tìm thấy file PDF tại: {pdf_path}")

        doc = fitz.open(pdf_path)
        pages_data = []

        for page_idx in range(len(doc)):
            page = doc[page_idx]
            text = page.get_text("text")
            pages_data.append({
                "page_num": page_idx + 1,
                "text": text
            })

        doc.close()
        return self._build_structure(pages_data, doc_source=os.path.basename(pdf_path))

    def parse_text(self, full_text: str, doc_name: str = "document") -> Dict[str, Any]:
        """
        Đọc và phân tích chuỗi văn bản thô.
        """
        pages_data = [{"page_num": 1, "text": full_text}]
        return self._build_structure(pages_data, doc_source=doc_name)

    def _build_structure(self, pages_data: List[Dict[str, Any]], doc_source: str) -> Dict[str, Any]:
        """
        Xây dựng cây phả hệ văn bản: Metadata -> Chương -> Điều -> Khoản -> Điểm.
        """
        doc_structure = {
            "source": doc_source,
            "total_pages": len(pages_data),
            "title": "",
            "doc_number": "",
            "articles": {},     # Dict theo số Điều: "Điều 1", "Điều 2"...
            "full_raw_text": "",
            "articles_order": [] # Thứ tự các điều
        }

        current_chuong = "Chung"
        current_muc = ""
        current_dieu_key = None
        current_khoan_key = None

        full_text_lines = []

        for p_info in pages_data:
            page_num = p_info["page_num"]
            raw_text = p_info["text"]
            lines = raw_text.splitlines()

            for line in lines:
                clean_line = line.strip()
                if not clean_line:
                    continue

                full_text_lines.append(clean_line)

                # 1. Kiểm tra Chương
                m_chuong = self.RE_CHUONG.match(clean_line)
                if m_chuong:
                    current_chuong = clean_line
                    continue

                # 2. Kiểm tra Mục
                m_muc = self.RE_MUC.match(clean_line)
                if m_muc:
                    current_muc = clean_line
                    continue

                # 3. Kiểm tra Điều
                m_dieu = self.RE_DIEU.match(clean_line)
                if m_dieu:
                    dieu_num = m_dieu.group(2)
                    dieu_title = m_dieu.group(3).strip()
                    current_dieu_key = f"Điều {dieu_num}"
                    current_khoan_key = None

                    if current_dieu_key not in doc_structure["articles"]:
                        doc_structure["articles_order"].append(current_dieu_key)
                        doc_structure["articles"][current_dieu_key] = {
                            "id": current_dieu_key,
                            "number": int(dieu_num) if dieu_num.isdigit() else dieu_num,
                            "title": dieu_title,
                            "chapter": current_chuong,
                            "section": current_muc,
                            "page_start": page_num,
                            "full_text": clean_line,
                            "clauses": {},
                            "raw_lines": [clean_line]
                        }
                    continue

                # Nếu đang nằm trong 1 Điều nào đó
                if current_dieu_key and current_dieu_key in doc_structure["articles"]:
                    art_obj = doc_structure["articles"][current_dieu_key]
                    art_obj["raw_lines"].append(clean_line)
                    art_obj["full_text"] += "\n" + clean_line

                    # 4. Kiểm tra Khoản (Ví dụ: "1. Hồ sơ gồm có...")
                    m_khoan = self.RE_KHOAN.match(clean_line)
                    if m_khoan and len(clean_line) > 3 and not clean_line.startswith(tuple("0123456789/")):
                        khoan_num = m_khoan.group(1)
                        khoan_body = m_khoan.group(2).strip()
                        current_khoan_key = f"Khoản {khoan_num}"

                        if current_khoan_key not in art_obj["clauses"]:
                            art_obj["clauses"][current_khoan_key] = {
                                "id": current_khoan_key,
                                "number": khoan_num,
                                "text": khoan_body,
                                "page": page_num,
                                "points": {}
                            }
                        continue

                    # 5. Kiểm tra Điểm (Ví dụ: "a) Giấy phép...")
                    m_diem = self.RE_DIEM.match(clean_line)
                    if m_diem and current_khoan_key and current_khoan_key in art_obj["clauses"]:
                        diem_id = m_diem.group(1).lower()
                        diem_body = m_diem.group(2).strip()
                        art_obj["clauses"][current_khoan_key]["points"][f"Điểm {diem_id}"] = {
                            "id": f"Điểm {diem_id}",
                            "text": diem_body,
                            "page": page_num
                        }
                        continue

        doc_structure["full_raw_text"] = "\n".join(full_text_lines)
        return doc_structure

    @staticmethod
    def extract_amendment_articles(amendment_text: str) -> List[Dict[str, Any]]:
        """
        Bóc tách nhanh các chỉ thị sửa đổi từ văn bản sửa đổi bổ sung.
        Ví dụ: "1. Sửa đổi, bổ sung Điều 15 như sau: ..." hoặc "2. Bãi bỏ Khoản 3 Điều 20."
        """
        results = []
        pattern = re.compile(
            r'(Sửa đổi\, bổ sung|Bãi bỏ|Thay thế|Bổ sung)\s+(Điều\s+\d+|Khoản\s+\d+\s+Điều\s+\d+|Điểm\s+[a-zđ]\s+Khoản\s+\d+\s+Điều\s+\d+)',
            re.IGNORECASE
        )
        for match in pattern.finditer(amendment_text):
            action_type = match.group(1).strip().title()
            target_unit = match.group(2).strip()
            results.append({
                "action": action_type,
                "target": target_unit,
                "position": match.start()
            })
        return results
