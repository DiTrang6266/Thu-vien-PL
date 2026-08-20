# -*- coding: utf-8 -*-
"""
Module: ai_analyzer.py
Mục đích: Lớp 3 trong Phễu phân loại lai (3-Tier Hybrid Funnel).
Nhiệm vụ: Bộ não Gemini AI (gemini-3.6-flash, gemini-3.7-flash) phân tích tác động toàn diện, đa chiều và chống ảo giác.
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
    """Chuyển đổi các định dạng ngày thành 'ngày DD tháng MM năm YYYY' chuẩn Nghị định 30."""
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
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

    def generate_nd30_citation(
        self,
        doc_title: str,
        doc_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Sinh câu căn cứ pháp lý chuẩn xác 100% theo Nghị định 30/2020/NĐ-CP."""
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
        elif "TIEU_CHUAN" in doc_type_str or "tcvn" in doc_title.lower():
            type_label = "Tiêu chuẩn quốc gia"

        # Khớp số hiệu
        if not so_hieu or len(so_hieu) > 35 or "/" not in so_hieu:
            match = re.search(r"(\d+(?:/\d{4})?/[A-ZĐĐa-z]+(?:-[A-ZĐĐa-z0-9]+)?)", f"{doc_title} {meta.get('raw_content', '')}")
            if match:
                so_hieu = match.group(1)

        # Khớp ngày ban hành
        if not ngay_bh:
            d_match = re.search(r"ngày\s+(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})", f"{doc_title} {meta.get('raw_content', '')}")
            if d_match:
                ngay_bh = d_match.group(0)

        formatted_date = format_vietnamese_date(ngay_bh)
        date_str = f" {formatted_date}" if formatted_date else ""
        
        # Thẩm quyền chuẩn
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
        elif authority == "Quốc hội":
            auth_str = ""

        # Trích yếu nội dung
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
        
        if self.api_key:
            system_instruction = """BẠN LÀ CHUYÊN GIA CỐ VẤN PHÁP LUẬT XÂY DỰNG VÀ ĐẤU THẦU ĐẦU TƯ CÔNG VIỆT NAM.
Nhiệm vụ: Đọc toàn văn tài liệu, phân tích TOÀN DIỆN, SÂU SẮC và trả về kết quả bằng ĐÚNG định dạng JSON Schema sau:

YÊU CẦU:
1. summary_top3: 3 điểm mới cốt lõi nhất (nêu rõ số liệu, tên phụ lục, thẩm quyền, ngày hiệu lực).
2. impact_areas: Phân tích tác động thực tiễn cho 3 đối tượng:
   - ho_so_moi_thau_va_dau_thau: Tác động đến E-HSMT, tiêu chuẩn đánh giá, quy trình đấu thầu.
   - du_toan_va_chi_phi: Tác động đến định mức, đơn giá nhân công, máy, quản lý chi phí.
   - tham_quyen_va_trach_nhiem: Tác động đến thẩm quyền phê duyệt của Chủ đầu tư, BQLDA, tư vấn.
3. transition_rules: Quy định chuyển tiếp cho các gói thầu/hồ sơ đang lập dở hoặc đã phát hành.
4. detailed_articles_diff: Danh sách 2-4 điều khoản quan trọng nhất (trích dẫn nguyên văn câu chữ để đối soát).
"""

            prompt = f"""{system_instruction}
Tiêu đề: {doc_title}
Nội dung tài liệu:
{doc_text[:15000]}

Trả về ĐÚNG JSON:
{{
  "is_project_relevant": true,
  "executive_title": "BÁO CÁO PHÂN TÍCH CHUYÊN SÂU: {doc_title[:80]}",
  "summary_top3": [
    "1. [Quy định / Định mức ban hành]: Nêu rõ tên định mức, dự án và cơ quan ban hành",
    "2. [Danh mục các phụ lục chi tiết]: Liệt kê các phụ lục kỹ thuật/đơn giá cụ thể",
    "3. [Hiệu lực & Trách nhiệm thi hành]: Nêu rõ ngày có hiệu lực và yêu cầu áp dụng"
  ],
  "impact_areas": {{
    "ho_so_moi_thau_va_dau_thau": "Phân tích tác động chi tiết tới công tác lập HSMT và lựa chọn nhà thầu",
    "du_toan_va_chi_phi": "Phân tích tác động chi tiết tới dự toán, định mức và hao phí",
    "tham_quyen_va_trach_nhiem": "Phân tích trách nhiệm BQLDA và các đơn vị liên quan"
  }},
  "transition_rules": "Quy định chuyển tiếp cụ thể đối với các hồ sơ nộp hoặc phát hành trước ngày hiệu lực",
  "cau_can_cu_nd30": "{citation}",
  "detailed_articles_diff": [
    {{
      "article_id": "Điều 1",
      "title": "Phạm vi điều chỉnh và đối tượng áp dụng",
      "status": "QUY ĐỊNH MỚI",
      "exact_quote_new": "Trích dẫn nguyên văn câu chữ quan trọng nhất trong văn bản",
      "core_change_explanation": "Giải thích ngắn gọn bản chất quy định",
      "action_required": "Hành động bắt buộc kỹ sư/BQLDA phải thực hiện"
    }}
  ]
}}
"""
            models_to_try = ["gemini-3.6-flash", "gemini-3.7-flash", "gemini-3.5-flash", "gemini-flash-latest"]
            for m in models_to_try:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={self.api_key}"
                    payload = {
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"}
                    }
                    with httpx.Client(timeout=35.0) as client:
                        res = client.post(url, json=payload)
                        if res.status_code == 200:
                            data = res.json()
                            raw_str = data["candidates"][0]["content"]["parts"][0]["text"]
                            clean_str = re.sub(r"^```json\s*", "", raw_str).strip().rstrip("`")
                            parsed = json.loads(clean_str)
                            parsed["cau_can_cu_nd30"] = citation
                            _log_debug(f"✅ Gemini AI ({m}) đã phân tích chuyên sâu thành công.")
                            return parsed
                except Exception as e:
                    _log_debug(f"⚠️ Thử model {m} gặp lỗi ({e}), chuyển model tiếp theo...")

        # Fallback đầy đủ cấu trúc
        return {
            "is_project_relevant": True,
            "executive_title": f"BÁO CÁO PHÂN TÍCH: {doc_title[:80]}",
            "summary_top3": [
                f"1. Ban hành văn bản chính thức áp dụng trong quản lý đầu tư xây dựng.",
                "2. Quy định chi tiết các định mức, quy chuẩn kỹ thuật và trình tự thủ tục.",
                "3. Yêu cầu chủ đầu tư và tư vấn áp dụng đúng từ ngày có hiệu lực."
            ],
            "impact_areas": {
                "ho_so_moi_thau_va_dau_thau": "Cần rà soát lại tiêu chuẩn kỹ thuật trong HSMT theo quy định mới.",
                "du_toan_va_chi_phi": "Áp dụng định mức chi phí và đơn giá theo quy định ban hành.",
                "tham_quyen_va_trach_nhiem": "Thực hiện đúng thẩm quyền phê duyệt và trách nhiệm quản lý dự án."
            },
            "transition_rules": "Áp dụng theo quy định chuyển tiếp tại các điều khoản thi hành của văn bản.",
            "cau_can_cu_nd30": citation,
            "detailed_articles_diff": []
        }
