import time
# -*- coding: utf-8 -*-
"""
Module: ai_analyzer.py
Mục đích: Động cơ AI Thẩm định & Phân tích Tác động Pháp lý Chuyên sâu (Executive Legal Impact Engine).
Tạo ra Báo cáo Tham mưu Chuyên môn Thực chiến cho Lãnh đạo Ban QLDA, Kỹ sư Dự toán, Cán bộ Đấu thầu và Kế toán:
1. Bảng Thông số, Định mức, Tỷ lệ %, Thời hạn và Biểu mẫu cụ thể.
2. Tác động trực tiếp đến việc Lập Dự toán, E-HSMT, Nghiệm thu, Sửa chữa tài sản công.
3. Bảng đối chiếu Cũ vs Mới (Redline Diff).
4. Cảnh báo rủi ro pháp lý & Điểm dễ bị Thanh tra/Kiểm toán bắt bẻ.
"""

import os
import json
import re
from typing import Dict, List, Any, Optional
import httpx


def _log_debug(msg: str):
    print(f"[{msg}]")
    try:
        log_path = os.path.join(os.path.dirname(__file__), "..", "data", "nhat_ky_trinh_sat.log")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"{msg}\n")
    except Exception:
        pass


def format_vietnamese_date(raw_date: str) -> str:
    if not raw_date:
        return ""
    if "tháng" in raw_date and "năm" in raw_date:
        return raw_date.strip()

    m = re.search(r"(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})", raw_date)
    if m:
        d, mon, y = int(m.group(1)), int(m.group(2)), m.group(3)
        return f"ngày {d:02d} tháng {mon:02d} năm {y}"
    return raw_date.strip()


class LegalAIAnalyzer:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or "AQ.Ab8RN6Ip2cJuK3UlMGyv6iWxuOEoiKyHo1oB61Fbx5b9oLNdqw"

    def generate_nd30_citation(
        self,
        doc_title: str,
        doc_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        meta = doc_metadata or {}
        so_hieu = meta.get("doc_number", "")
        doc_type = meta.get("doc_type", "THÔNG TƯ")
        authority = meta.get("authority", "Bộ Xây dựng")
        ngay_bh = meta.get("ngay_ban_hanh", "")

        type_label = "Thông tư"
        doc_type_str = str(doc_type).upper()
        if "VAN_BAN_HOP_NHAT" in doc_type_str or "VBHN" in doc_title.upper() or "HỢP NHẤT" in doc_title.upper():
            type_label = "Văn bản hợp nhất"
        elif "NGHI_DINH" in doc_type_str or "nghị định" in doc_title.lower():
            type_label = "Nghị định"
        elif "THONG_TU" in doc_type_str or "thông tư" in doc_title.lower():
            type_label = "Thông tư"
        elif "QUYET_DINH" in doc_type_str or "quyết định" in doc_title.lower():
            type_label = "Quyết định"
        elif "LUAT" in doc_type_str or "luật" in doc_title.lower():
            type_label = "Luật"
        elif "QUY_CHUAN" in doc_type_str or "qcvn" in doc_title.lower():
            type_label = "Quy chuẩn kỹ thuật quốc gia"

        if not so_hieu or len(so_hieu) > 35 or "/" not in so_hieu:
            match = re.search(r"(\d+(?:/\d{4})?/[A-ZĐĐa-z]+(?:-[A-ZĐĐa-z0-9]+)?)", f"{doc_title} {meta.get('raw_content', '')}")
            if match:
                so_hieu = match.group(1)

        if not ngay_bh:
            d_match = re.search(r"ngày\s+(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})", f"{doc_title} {meta.get('raw_content', '')}")
            if d_match:
                ngay_bh = d_match.group(0)

        formatted_date = format_vietnamese_date(ngay_bh)
        date_str = f" {formatted_date}" if formatted_date else ""
        
        auth_str = f" của {authority}"
        if authority == "Bộ Xây dựng":
            auth_str = " của Bộ trưởng Bộ Xây dựng"
        elif authority == "Bộ Kế hoạch và Đầu tư":
            auth_str = " của Bộ trưởng Bộ Kế hoạch và Đầu tư"
        elif authority == "Bộ Quốc phòng":
            auth_str = " của Bộ trưởng Bộ Quốc phòng"
        elif authority == "Bộ Tài chính":
            auth_str = " của Bộ trưởng Bộ Tài chính"
        elif authority == "Chính phủ":
            auth_str = " của Chính phủ"
        elif authority == "Thủ tướng Chính phủ":
            auth_str = " của Thủ tướng Chính phủ"

        trich_yeu = doc_title.strip()
        trich_yeu = re.sub(r"^(Thông tư|Nghị định|Quyết định|Luật|Văn bản hợp nhất)\s*(số\s*[\w\-/]+)?\s*", "", trich_yeu, flags=re.IGNORECASE)
        trich_yeu = re.sub(r"^ngày\s*[\d/.\-]+\s*", "", trich_yeu, flags=re.IGNORECASE)
        trich_yeu = trich_yeu.strip()
        if trich_yeu:
            trich_yeu = trich_yeu[0].lower() + trich_yeu[1:] if len(trich_yeu) > 1 else trich_yeu

        if so_hieu and "/" in so_hieu:
            return f"Căn cứ {type_label} số {so_hieu}{date_str}{auth_str} {trich_yeu};"
        else:
            return f"Căn cứ {type_label}{date_str}{auth_str} {trich_yeu};"

    def analyze_document_deep(
        self,
        doc_text: str,
        doc_title: str,
        doc_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        citation = self.generate_nd30_citation(doc_title, doc_metadata)
        
        system_instruction = """BẠN LÀ CHUYÊN GIA THẨM ĐỊNH PHÁP LUẬT VÀ TƯ VẤN QUẢN LÝ DỰ ÁN XÂY DỰNG / ĐẤU THẦU CAO CẤP.
Nhiệm vụ: Lập BẢN BÁO CÁO THAM MƯU TÁC ĐỘNG NGHIỆP VỤ THỰC CHIẾN (EXECUTIVE IMPACT REPORT) cho Giám đốc Ban QLDA, Kỹ sư Dự toán, Cán bộ Đấu thầu và Kế toán tài sản công.

1. THẨM ĐỊNH GÁC CỔNG NGHIÊM NGẶT:
   - Văn bản PHẢI thuộc 1 trong 4 Trụ cột Nghiệp vụ Thực chiến:
     (1) Quản lý đầu tư xây dựng & Quản lý dự án (Dự toán, định mức, chi phí, quản lý chất lượng, an toàn thi công, nghiệm thu).
     (2) Đấu thầu & Lựa chọn nhà thầu (E-HSMT, KHLCNT, hợp đồng xây dựng, chỉ định thầu, chấm thầu).
     (3) Chi thường xuyên & Mua sắm/Sửa chữa tài sản công (NĐ 138/2024, NĐ 114/2024, cải tạo, bảo dưỡng trụ sở, máy móc).
     (4) Công trình Quốc phòng & PCCC công trình (QCVN 06, công trình quân sự).
   - NẾU LÀ MẢNG QUY HOẠCH ĐÔ THỊ/NÔNG THÔN VĨ MÔ, HÀNG HẢI, HOA TIÊU, VẬN TẢI, Y TẾ, HOẶC DỰ ÁN RIÊNG: ĐÁNH DẤU "is_domain_relevant": false VÀ DỪNG LẠI.

2. NỘI DUNG BÁO CÁO THAM MƯU THỰC CHIẾN (CHỐNG TÓM TẮT SƠ SÀI / KHÔNG NÓI CHUNG CHUNG):
   - TÁC ĐỘNG HỒ SƠ DỰ ÁN: Chỉ rõ văn bản tác động cụ thể đến việc Lập Dự toán (thay đổi định mức/hệ số/đơn giá nào?), Hồ sơ mời thầu (tiêu chí nào mới, mẫu nào áp dụng?), hay Nghiệm thu thanh toán.
   - BẢNG ĐỐI CHIẾU THAY ĐỔI CŨ VS MỚI (REDLINE): Nêu rõ Quy định cũ là gì -> Quy định mới sửa thành gì -> Khác biệt trọng yếu.
   - THÔNG SỐ VÀ CON SỐ CỤ THỂ: Trích xuất chính xác các con số %, thời hạn (số ngày), số tiền, số lượng bộ hồ sơ hoặc biểu mẫu Phụ lục bắt buộc.
   - CẢNH BÁO RỦI RO & BẪY PHÁP LÝ: Nêu rõ điểm dễ bị Thanh tra, Kiểm toán Nhà nước bắt bẻ hoặc xuất toán, và cách xử lý hồ sơ/gói thầu đang làm dở (Điều khoản chuyển tiếp).
   - BẮT BUỘC TRÍCH DẪN ĐIỀU KHOẢN: Mọi nhận định đều phải ghi rõ [Điều X Khoản Y].
"""

        prompt = f"""{system_instruction}
Tiêu đề văn bản: {doc_title}
Toàn văn tài liệu:
{doc_text[:35000]}

Trả về ĐÚNG định dạng JSON sau (không thêm bất kỳ ký tự nào ngoài JSON):
{{
  "is_domain_relevant": true,
  "is_nationwide_universal": true,
  "scope_explanation": "Giải thích vì sao văn bản thuộc 4 trụ cột thực chiến",
  "is_project_relevant": true,
  "executive_title": "BÁO CÁO THAM MƯU NGHIỆP VỤ: {doc_title[:80]}",
  "impact_summary": "Đoạn văn 3-4 câu phân tích tổng quan tác động trực tiếp đến Ban QLDA, Chủ đầu tư và Nhà thầu",
  "substantive_points": [
    {{
      "clause": "[Điều ... Khoản ...]",
      "title": "Tên nội dung quy định cụ thể",
      "content": "Phân tích chi tiết 2-3 câu về nội dung quy định, kèm thông số %, định mức, biểu mẫu hoặc thời hạn cụ thể",
      "action_required": "Hành động bắt buộc: Kỹ sư/Cán bộ dự án phải làm gì (sửa hồ sơ, áp dụng mẫu mới, điều chỉnh dự toán...)"
    }}
  ],
  "comparative_table": [
    {{
      "item": "Nội dung quy định",
      "old_rule": "Quy định cũ trước đây",
      "new_rule": "Quy định mới sửa đổi/ban hành",
      "key_difference": "Điểm khác biệt trọng yếu"
    }}
  ],
  "repealed_docs": [
    "Số hiệu và tên đầy đủ của văn bản cũ bị bãi bỏ hoặc thay thế"
  ],
  "compliance_risks": "Cảnh báo các rủi ro pháp lý, điểm dễ bị Thanh tra/Kiểm toán bắt lỗi và lưu ý xử lý hồ sơ đang dở dang",
  "effective_and_transition": "Quy định chi tiết về ngày có hiệu lực và điều khoản chuyển tiếp",
  "cau_can_cu_nd30": "{citation}"
}}
"""
        models_to_try = [
            "gemini-2.5-flash",
            "gemini-3.5-flash",
            "gemini-2.5-flash-lite",
            "gemini-flash-latest",
            "gemini-3.5-flash-lite",
            "gemini-2.5-pro"
        ]
        for m in models_to_try:
            for attempt in range(2):
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={self.api_key}"
                    payload = {
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {"temperature": 0.0, "responseMimeType": "application/json"}
                    }
                    with httpx.Client(timeout=45.0) as client:
                        res = client.post(url, json=payload)
                        if res.status_code == 200:
                            data = res.json()
                            raw_str = data["candidates"][0]["content"]["parts"][0]["text"]
                            clean_str = re.sub(r"^```json\s*", "", raw_str).strip().rstrip("`")
                            parsed = json.loads(clean_str)
                            parsed["cau_can_cu_nd30"] = citation
                            
                            is_domain = parsed.get("is_domain_relevant", True)
                            is_universal = parsed.get("is_nationwide_universal", True)

                            if not is_domain or not is_universal:
                                parsed["is_project_relevant"] = False
                                _log_debug(f"ℹ️ Gemini AI ({m}) đã lọc bỏ: Domain={is_domain}, Universal={is_universal} ({parsed.get('scope_explanation')})")
                            else:
                                parsed["is_project_relevant"] = True
                                _log_debug(f"✅ Gemini AI ({m}) đã lập Báo cáo Tham mưu Nghiệp vụ Chuyên sâu thành công.")
                            
                            return parsed
                        elif res.status_code == 429:
                            _log_debug(f"⏳ Model {m} bị giới hạn tốc độ (429), chờ 3 giây rồi thử lại...")
                            time.sleep(3.0)
                        else:
                            _log_debug(f"⚠️ Model {m} trả về status {res.status_code}, đổi model...")
                            break
                except Exception as e:
                    _log_debug(f"⚠️ Model {m} gặp ngoại lệ ({e}), thử model tiếp theo...")
                    time.sleep(1.0)
                    break

        # Fallback an toàn
        return {
            "is_domain_relevant": True,
            "is_nationwide_universal": True,
            "scope_explanation": "Văn bản chuyên ngành quản lý xây dựng",
            "is_project_relevant": True,
            "executive_title": f"BÁO CÁO THAM MƯU: {doc_title[:80]}",
            "impact_summary": f"Văn bản {doc_title} ban hành quy định áp dụng trong công tác quản lý dự án và đầu tư xây dựng.",
            "substantive_points": [
                {
                    "clause": "[Toàn văn]",
                    "title": "Áp dụng theo quy định ban hành",
                    "content": "Thực hiện theo các điều khoản và thông số kỹ thuật chi tiết ban hành kèm theo văn bản.",
                    "action_required": "Rà soát hồ sơ dự án để áp dụng đúng quy định hiện hành."
                }
            ],
            "comparative_table": [],
            "repealed_docs": [],
            "compliance_risks": "Tuân thủ chặt chẽ ngày hiệu lực để tránh rủi ro pháp lý khi thanh quyết toán.",
            "effective_and_transition": "Thực hiện theo điều khoản thi hành của văn bản.",
            "cau_can_cu_nd30": citation
        }
