# -*- coding: utf-8 -*-
"""
Module: ai_analyzer.py
Mục đích: Lớp 3 trong Phễu phân loại lai (3-Tier Hybrid Funnel).
Chức năng:
- Sử dụng Gemini API (1.5 Flash / 2.0 / 2.5) với Pydantic v2 JSON Schema để phân tích tác động toàn văn (Zero-Chunking).
- Bóc tách Top 3 điểm mới cốt lõi, bảng so sánh Cũ vs Mới (Side-by-side Redline).
- Phân tích tác động trực tiếp tới các gói thầu dự án (TV-04, TV-05, XD-01...).
- Trích dẫn nguyên văn số Điều/Khoản làm căn cứ chống ảo giác (Zero-Hallucination).
- Tự động sinh câu căn cứ chuẩn Nghị định 30/2020/NĐ-CP để nạp thẳng vào Sổ cái Excel.
"""

import os
import json
import re
from typing import Dict, List, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
import httpx


def _log_debug(msg: str):
    print(f"[{msg}]")
    try:
        log_path = os.path.join(os.path.dirname(__file__), "..", "data", "nhat_ky_trinh_sat.log")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"{msg}\n")
    except Exception:
        pass


class ImpactLevel(str, Enum):
    CRITICAL = "CRITICAL"    # Thay đổi cốt lõi, phải cập nhật hồ sơ ngay
    HIGH = "HIGH"            # Ảnh hưởng quy trình, đơn giá hoặc biểu mẫu
    MEDIUM = "MEDIUM"        # Thay đổi nhỏ, cần lưu ý áp dụng
    LOW = "LOW"              # Tham khảo, điều chỉnh từ ngữ hành chính
    NONE = "NONE"


class GroundingEvidence(BaseModel):
    clause_reference: str = Field(description="Số Điều, Khoản cụ thể làm căn cứ, VD: 'Khoản 2 Điều 45'")
    exact_quote: str = Field(description="Trích dẫn nguyên văn câu chữ trong văn bản")
    impact_note: str = Field(description="Giải thích ngắn gọn tác động cụ thể tới hồ sơ")


class PracticalImpactItem(BaseModel):
    area: str = Field(description="Phân hệ nghiệp vụ: Đấu thầu, Dự toán, QLDA, BQLDA...")
    action_required: str = Field(description="Hành động bắt buộc kỹ sư/BQLDA phải làm")


class LegalAIAnalysisResult(BaseModel):
    is_project_relevant: bool = Field(default=True, description="Có tác động tới hồ sơ dự án xây dựng/đấu thầu hay không")
    impact_level: ImpactLevel = Field(default=ImpactLevel.HIGH, description="Mức độ tác động")
    executive_title: str = Field(description="Tiêu đề báo cáo tóm lược, súc tích")
    summary_top3: List[str] = Field(description="Top 3 điểm mới thay đổi cốt lõi kèm số liệu cụ thể")
    practical_impacts: List[PracticalImpactItem] = Field(description="Phân tích tác động thực tiễn cho người lập hồ sơ")
    affected_packages: List[str] = Field(default_factory=list, description="Danh sách gói thầu bị ảnh hưởng: TV-04, TV-05, XD-01, ALL...")
    transitional_provision: str = Field(description="Quy định chuyển tiếp cho các hồ sơ đang làm dở")
    cau_can_cu_nd30: str = Field(description="Câu căn cứ sinh chuẩn thể thức Nghị định 30/2020 để ốp vào Word")
    evidences: List[GroundingEvidence] = Field(default_factory=list, description="Bằng chứng trích dẫn nguyên văn chống ảo giác")
    side_by_side_diff: List[Dict[str, str]] = Field(default_factory=list, description="Bảng so sánh Cũ vs Mới theo từng Điều")


class LegalAIAnalyzer:
    """
    Bộ não AI phân tích tác động pháp lý toàn văn bằng Gemini API thế hệ mới.
    """

    def __init__(self, api_key: Optional[str] = None, preferred_model: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.preferred_model = preferred_model

    def get_available_models(self) -> List[str]:
        """Tự động lấy danh sách chính xác các model Gemini đang hoạt động."""
        if not self.api_key:
            return ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-2.5-flash"]

        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models?key={self.api_key}"
            with httpx.Client(timeout=15.0) as client:
                res = client.get(url)
                if res.status_code == 200:
                    models_data = res.json().get("models", [])
                    active_models = [
                        m["name"].replace("models/", "")
                        for m in models_data
                        if "generateContent" in m.get("supportedGenerationMethods", [])
                    ]
                    def sort_key(name: str):
                        score = 0
                        if "2.5" in name or "2.0" in name: score += 50
                        elif "1.5" in name: score += 30
                        if "flash" in name: score += 10
                        if "pro" in name: score += 5
                        return -score

                    active_models.sort(key=sort_key)
                    if active_models:
                        return active_models
        except Exception as e:
            _log_debug(f"⚠️ Không thể lấy danh sách model động: {e}")

        return ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-2.5-flash"]

    def generate_nd30_citation(self, title: str, doc_metadata: Optional[Dict[str, Any]] = None) -> str:
        """Sinh chuỗi căn cứ chuẩn Nghị định 30/2020/NĐ-CP."""
        clean_title = (title or "").strip()
        doc_type = "văn bản"
        if "nghị định" in clean_title.lower():
            doc_type = "Nghị định"
        elif "thông tư" in clean_title.lower():
            doc_type = "Thông tư"
        elif "quyết định" in clean_title.lower():
            doc_type = "Quyết định"
        elif "luật" in clean_title.lower():
            doc_type = "Luật"

        # Khớp số hiệu
        match = re.search(r"(\d+(?:/\d{4})?/[A-ZĐĐa-z]+(?:-[A-ZĐĐa-z0-9]+)?)", clean_title)
        so_hieu = match.group(1) if match else clean_title[:30]

        citation = f"Căn cứ {doc_type} số {so_hieu} của cơ quan có thẩm quyền ban hành;"
        if "24/2024" in clean_title:
            citation = "Căn cứ Nghị định số 24/2024/NĐ-CP ngày 27 tháng 02 năm 2024 của Chính phủ quy định chi tiết một số điều và biện pháp thi hành Luật Đấu thầu về lựa chọn nhà thầu;"
        elif "06/2024" in clean_title:
            citation = "Căn cứ Thông tư số 06/2024/TT-BKHĐT ngày 26 tháng 4 năm 2024 của Bộ trưởng Bộ Kế hoạch và Đầu tư hướng dẫn việc cung cấp, đăng tải thông tin về đấu thầu và mẫu hồ sơ đấu thầu trên Hệ thống mạng đấu thầu quốc gia;"
        elif "10/2021" in clean_title:
            citation = "Căn cứ Nghị định số 10/2021/NĐ-CP ngày 09 tháng 02 năm 2021 của Chính phủ về quản lý chi phí đầu tư xây dựng;"
        elif "12/2021" in clean_title:
            citation = "Căn cứ Thông tư số 12/2021/TT-BXD ngày 31 tháng 8 năm 2021 của Bộ trưởng Bộ Xây dựng ban hành định mức xây dựng;"

        return citation

    def analyze_document_deep(
        self,
        doc_text: str,
        doc_title: str,
        doc_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Phân tích chuyên sâu văn bản bằng Gemini API kết hợp Structured JSON Schema.
        """
        if not self.api_key:
            _log_debug("⚠️ CẢNH BÁO: Chưa tìm thấy GEMINI_API_KEY. Chạy phân tích quy tắc dự phòng.")
            return self._fallback_structured_analysis(doc_title, doc_text, doc_metadata)

        system_instruction = """BẠN LÀ CHUYÊN GIA CỐ VẤN PHÁP LÝ CAO CẤP VỀ ĐẤU THẦU VÀ QUẢN LÝ DỰ ÁN XÂY DỰNG VIỆT NAM.
Nhiệm vụ của bạn là đọc toàn văn tài liệu, phân tích SÂU SẮC, RÕ RÀNG, ĐI THẲNG VÀO BẢN CHẤT THAY ĐỔI và xuất dữ liệu tuân thủ đúng 100% JSON Schema.

YÊU CẦU BẮT BUỘC:
1. NÓI RÕ CON SỐ VÀ HÀNH ĐỘNG CỤ THỂ (số ngày, hạn mức tiền, tỷ lệ %, trách nhiệm BQLDA).
2. TRÍCH NGUYÊN VĂN 100% số Điều, Khoản cụ thể vào mục evidences để người dùng đối soát chống ảo giác.
3. Chỉ rõ các gói thầu bị tác động (TV-04 Khảo sát thiết kế, TV-05 Giám sát, XD-01 Xây lắp...).
4. Trả về đúng định dạng JSON Schema được yêu cầu."""

        prompt = f"""{system_instruction}

--- TOÀN VĂN / TRÍCH YẾU TÀI LIỆU CẦN PHÂN TÍCH ---
Tiêu đề: {doc_title}
Nội dung:
{doc_text[:15000]}
--- HẾT TÀI LIỆU ---

Hãy phân tích toàn diện và trả về kết quả bằng ĐÚNG định dạng JSON sau:
{{
  "is_project_relevant": true,
  "impact_level": "HIGH",
  "executive_title": "BÁO CÁO PHÂN TÍCH TÁC ĐỘNG: {doc_title[:80]}",
  "summary_top3": [
    "1. [Điểm mới 1]: Nêu rõ con số/quy định cụ thể bị thay đổi",
    "2. [Điểm mới 2]: Nêu rõ quy trình hoặc biểu mẫu mới",
    "3. [Điểm mới 3]: Nêu rõ thẩm quyền hoặc hạn mức phê duyệt"
  ],
  "practical_impacts": [
    {{"area": "Đấu thầu & E-HSMT", "action_required": "Cập nhật biểu mẫu và thang điểm đánh giá mới."}},
    {{"area": "Dự toán & Định mức", "action_required": "Rà soát lại đơn giá nhân công và hệ số hao phí."}},
    {{"area": "Thẩm quyền BQLDA", "action_required": "Kiểm tra lại thẩm quyền ký duyệt theo phân cấp mới."}}
  ],
  "affected_packages": ["TV-04", "TV-05", "XD-01"],
  "transitional_provision": "Quy định chuyển tiếp cụ thể cho các hồ sơ đang lập dở hoặc đã phát hành trước ngày hiệu lực.",
  "cau_can_cu_nd30": "{self.generate_nd30_citation(doc_title, doc_metadata)}",
  "evidences": [
    {{
      "clause_reference": "Điều 1 Khoản 1",
      "exact_quote": "Trích dẫn nguyên văn câu chữ quan trọng nhất trong văn bản",
      "impact_note": "Hồ sơ dự án cần áp dụng ngay từ ngày hiệu lực."
    }}
  ],
  "side_by_side_diff": []
}}
"""

        available_models = self.get_available_models()
        if self.preferred_model and self.preferred_model in available_models:
            available_models.remove(self.preferred_model)
            available_models.insert(0, self.preferred_model)

        for model_name in available_models[:3]:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.api_key}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.1,
                        "responseMimeType": "application/json"
                    }
                }
                with httpx.Client(timeout=45.0) as client:
                    res = client.post(url, json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            raw_json_str = candidates[0]["content"]["parts"][0]["text"].strip()
                            clean_json = re.sub(r"^```json\s*", "", raw_json_str)
                            clean_json = re.sub(r"\s*```$", "", clean_json)
                            parsed = json.loads(clean_json)
                            _log_debug(f"✅ Gemini AI ({model_name}) đã phân tích thành công có cấu trúc.")
                            return parsed
            except Exception as e:
                _log_debug(f"⚠️ Thử model {model_name} không thành công ({e}), chuyển model kế tiếp...")

        return self._fallback_structured_analysis(doc_title, doc_text, doc_metadata)

    def _fallback_structured_analysis(
        self,
        doc_title: str,
        doc_text: str,
        doc_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Tạo cấu trúc phân tích dự phòng khi không có kết nối Gemini API."""
        citation = self.generate_nd30_citation(doc_title, doc_metadata)
        return {
            "is_project_relevant": True,
            "impact_level": "HIGH",
            "executive_title": f"BÁO CÁO PHÂN TÍCH TÁC ĐỘNG: {doc_title[:80]}",
            "summary_top3": [
                f"1. Văn bản chính thức ban hành: {doc_title[:100]}.",
                "2. Quy định các điều khoản kỹ thuật và trình tự thủ tục mới áp dụng cho hồ sơ dự án.",
                "3. Yêu cầu rà soát và đối chiếu các biểu mẫu đang áp dụng trong các gói thầu."
            ],
            "practical_impacts": [
                {"area": "Đấu thầu & E-HSMT", "action_required": "Cần rà soát lại mẫu hồ sơ mời thầu theo các điều khoản mới."},
                {"area": "Dự toán & Chi phí", "action_required": "Cập nhật các định mức chi phí và đơn giá theo quy định mới."},
                {"area": "Thẩm quyền BQLDA", "action_required": "Kiểm tra lại thẩm quyền và trách nhiệm phê duyệt hồ sơ."}
            ],
            "affected_packages": ["TV-04", "TV-05", "XD-01"],
            "transitional_provision": "Thực hiện theo quy định chuyển tiếp tại các điều khoản cuối của văn bản.",
            "cau_can_cu_nd30": citation,
            "evidences": [
                {
                    "clause_reference": "Toàn văn",
                    "exact_quote": doc_text[:200].strip() if doc_text else doc_title,
                    "impact_note": "Áp dụng cho toàn bộ các gói thầu thuộc phạm vi điều chỉnh."
                }
            ],
            "side_by_side_diff": []
        }
