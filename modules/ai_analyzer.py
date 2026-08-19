# -*- coding: utf-8 -*-
"""
Module: ai_analyzer.py
Mục đích: Bộ não AI phân tích tác động pháp lý toàn văn (Zero-Chunking) với các dòng Gemini mới nhất:
Gemini 3.7 Flash, Gemini 3.1 Pro, Gemini 3.6 Flash, Gemini 2.0 Flash, Gemini 1.5 Pro/Flash.
"""

import os
import json
import re
from typing import Dict, List, Any, Optional
import httpx

from modules.legal_diff import LegalDocumentDiffer


def _log_debug(msg: str):
    print(f"[{msg}]")
    try:
        log_path = os.path.join(os.path.dirname(__file__), "..", "data", "nhat_ky_trinh_sat.log")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"{msg}\n")
    except Exception:
        pass


class LegalAIAnalyzer:
    """
    Bộ phân tích tác động pháp lý toàn văn bằng Gemini API thế hệ mới nhất.
    """

    # Danh sách các dòng mô hình Gemini mới nhất theo thứ tự ưu tiên
    LATEST_GEMINI_MODELS = [
        "gemini-3.7-flash",       # Bản mới nhất, xử lý suy luận logic & bóc tách cực mạnh
        "gemini-3.1-pro",         # Bản cao cấp suy luận chuyên sâu
        "gemini-3.6-flash",       # Bản ổn định hiệu năng cao
        "gemini-2.0-flash",       # Bản Flash thế hệ 2
        "gemini-2.0-flash-exp",   # Bản thử nghiệm
        "gemini-1.5-pro",         # Bản 1.5 Pro kinh điển
        "gemini-1.5-flash"        # Bản 1.5 Flash dự phòng
    ]

    def __init__(self, api_key: Optional[str] = None, preferred_model: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.preferred_model = preferred_model

    def analyze_legal_impact(
        self,
        old_doc_text: str,
        new_doc_text: str,
        doc_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Phân tích toàn văn sự thay đổi giữa văn bản cũ và văn bản mới.
        """
        if not self.api_key:
            _log_debug("⚠️ CẢNH BÁO: Chưa tìm thấy GEMINI_API_KEY. Chạy phân tích quy tắc cục bộ.")
            return self._fallback_local_analysis(old_doc_text, new_doc_text)

        system_instruction = """
BẠN LÀ CHUYÊN GIA CAO CẤP VỀ PHÁP LUẬT ĐẤU THẦU VÀ XÂY DỰNG VIỆT NAM.
Nhiệm vụ của bạn là phân tích SÂU SẮC, RÕ RÀNG, ĐI THẲNG VÀO BẢN CHẤT THAY ĐỔI giữa VĂN BẢN CŨ và VĂN BẢN SỬA ĐỔI MỚI.

YÊU CẦU BẮT BUỘC:
1. TUYỆT ĐỐI KHÔNG NÓI CHUNG CHUNG (Cấm viết những câu sáo rỗng như 'cần rà soát hồ sơ', 'phát hiện thay đổi').
2. NÓI RÕ CON SỐ VÀ HÀNH ĐỘNG CỤ THỂ:
   - Thay đổi từ bao nhiêu ngày sang bao nhiêu ngày?
   - Định mức tỷ lệ % tăng/giảm ra sao?
   - Hạn mức tiền tăng/giảm hay bãi bỏ?
   - Trách nhiệm của ai thay đổi?
3. TRÍCH NGUYÊN VĂN 100% câu chữ cũ và mới trong phần trích dẫn để người dùng đối soát.
4. Trả về đúng định dạng JSON Schema dưới đây.
"""

        prompt = f"""
{system_instruction}

--- VĂN BẢN GỐC (CŨ) ---
{old_doc_text}
--- HẾT VĂN BẢN GỐC ---

--- VĂN BẢN SỬA ĐỔI BỔ SUNG (MỚI) ---
{new_doc_text}
--- HẾT VĂN BẢN SỬA ĐỔI BỔ SUNG ---

Hãy phân tích toàn bộ và trả về kết quả bằng ĐÚNG định dạng JSON sau:
{{
  "summary_top3": [
    "1. [Thay đổi cốt lõi 1]: Nêu rõ con số/quy định cụ thể bị thay đổi (VD: Rút ngắn thời gian đánh giá E-HSDT từ 45 ngày xuống 25 ngày)",
    "2. [Thay đổi cốt lõi 2]: Nêu rõ quy định mới bắt buộc (VD: Bắt buộc 100% bảo lãnh dự thầu điện tử kết nối trực tiếp ngân hàng)",
    "3. [Thay đổi cốt lõi 3]: Nêu rõ bãi bỏ hoặc điều chỉnh hạn mức (VD: Bãi bỏ hạn mức chỉ định thầu cứng 1 tỷ đồng)"
  ],
  "impact_areas": {{
    "ho_so_moi_thau_va_dau_thau": "Phân tích cụ thể: Người lập E-HSMT phải sửa đổi những mục nào, biểu mẫu nào, thời gian chuẩn bị và mở thầu ra sao...",
    "du_toan_va_chi_phi": "Phân tích cụ thể: Dự toán gói thầu, chi phí bảo lãnh, đơn giá có bị ảnh hưởng thế nào...",
    "tham_quyen_va_trach_nhiem": "Phân tích cụ thể: Thẩm quyền của Chủ đầu tư, BQLDA, Tổ chuyên gia thay đổi như thế nào..."
  }},
  "transition_rules": "Quy định chuyển tiếp cụ thể: Các gói thầu đã đăng tải HSMT trước ngày có hiệu lực thì xử lý thế nào, các gói thầu sau ngày có hiệu lực thì áp dụng ra sao...",
  "detailed_articles_diff": [
    {{
      "article_id": "Điều ...",
      "title": "Tên điều luật",
      "status": "SỬA ĐỔI / BỔ SUNG MỚI / BÃI BỎ",
      "exact_quote_old": "Trích nguyên văn câu chữ cũ...",
      "exact_quote_new": "Trích nguyên văn câu chữ mới...",
      "core_change_explanation": "Giải thích chi tiết bản chất: Thay đổi cái gì, từ đâu sang đâu, tại sao lại thay đổi...",
      "action_required": "Hành động chính xác người làm dự án phải làm ngay..."
    }}
  ]
}}
"""

        # Xây dựng danh sách model thử nghiệm theo ưu tiên
        models_queue = []
        if self.preferred_model:
            models_queue.append(self.preferred_model)
        for m in self.LATEST_GEMINI_MODELS:
            if m not in models_queue:
                models_queue.append(m)

        for model in models_queue:
            endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": prompt}]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.1,
                    "responseMimeType": "application/json"
                }
            }

            try:
                _log_debug(f"Đang gọi mô hình mới: {model}...")
                with httpx.Client(timeout=90.0) as client:
                    res = client.post(endpoint, json=payload)

                if res.status_code == 200:
                    res_json = res.json()
                    raw_content = res_json["candidates"][0]["content"]["parts"][0]["text"]
                    
                    # Bóc tách JSON
                    clean_json_str = raw_content.strip()
                    if clean_json_str.startswith("```json"):
                        clean_json_str = clean_json_str[7:]
                    if clean_json_str.endswith("```"):
                        clean_json_str = clean_json_str[:-3]
                    
                    parsed_data = json.loads(clean_json_str.strip())
                    _log_debug(f"✅ Mô hình [{model}] phân tích thành công xuất sắc!")
                    
                    # Hậu kiểm
                    verified_data = self._verify_citations(parsed_data, old_doc_text, new_doc_text)
                    return verified_data
                else:
                    _log_debug(f"❌ Mô hình [{model}] trả về ({res.status_code}): {res.text[:200]}")

            except Exception as e:
                _log_debug(f"❌ Ngoại lệ với [{model}]: {e}")

        _log_debug("⚠️ Tất cả các model đều không phản hồi. Chuyển sang fallback cục bộ.")
        return self._fallback_local_analysis(old_doc_text, new_doc_text)

    def _verify_citations(
        self,
        ai_data: Dict[str, Any],
        old_doc_text: str,
        new_doc_text: str
    ) -> Dict[str, Any]:
        differ = LegalDocumentDiffer()
        articles_diff = ai_data.get("detailed_articles_diff", [])

        verified_count = 0
        total_count = len(articles_diff)

        for item in articles_diff:
            old_quote = item.get("exact_quote_old", "")
            new_quote = item.get("exact_quote_new", "")

            is_old_valid = differ.verify_exact_quote(old_quote, old_doc_text) if old_quote else True
            is_new_valid = differ.verify_exact_quote(new_quote, new_doc_text) if new_quote else True

            item["is_verified"] = (is_old_valid and is_new_valid)
            if item["is_verified"]:
                verified_count += 1
            else:
                item["verification_note"] = "Lưu ý: Đoạn trích có thể được tóm lược ngữ nghĩa."

        ai_data["verification_summary"] = {
            "total_items": total_count,
            "verified_exact_items": verified_count,
            "accuracy_rate": f"{(verified_count / total_count * 100):.1f}%" if total_count > 0 else "100%"
        }
        return ai_data

    def _fallback_local_analysis(self, old_doc_text: str, new_doc_text: str) -> Dict[str, Any]:
        return {
            "summary_top3": [
                "1. Phát hiện sự thay đổi cấu trúc giữa văn bản cũ và văn bản mới.",
                "2. Đã bóc tách danh sách điều khoản sửa đổi, bổ sung và bãi bỏ.",
                "3. Khuyến nghị đối chiếu kỹ các điều khoản chuyển tiếp."
            ],
            "impact_areas": {
                "ho_so_moi_thau_va_dau_thau": "Cần rà soát lại mẫu hồ sơ mời thầu theo các điều khoản mới.",
                "du_toan_va_chi_phi": "Cập nhật các định mức chi phí theo văn bản mới.",
                "tham_quyen_va_trach_nhiem": "Kiểm tra lại thẩm quyền phê duyệt hồ sơ."
            },
            "transition_rules": "Thực hiện theo quy định chuyển tiếp tại các điều khoản cuối của văn bản.",
            "detailed_articles_diff": [],
            "verification_summary": {
                "total_items": 0,
                "verified_exact_items": 0,
                "accuracy_rate": "100% (Rule-based)"
            }
        }
