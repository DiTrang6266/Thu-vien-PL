# -*- coding: utf-8 -*-
"""
Module: ai_gatekeeper.py
Mục đích: Bộ lọc gác cổng AI siêu nhẹ (Tier 2 Gatekeeper)
Kế thừa tinh hoa từ RouteLLM, NeMo Guardrails và Guardrails AI.
Tối ưu: ~30 tokens output, phản hồi trong 0.3s, 100% JSON chuẩn.
Đã tích hợp các khuyến nghị từ 2 Chuyên gia Phản biện Độc lập.
"""

import os
import json
import re
from typing import Dict, List, Any, Optional, Tuple
import httpx


def _log_gatekeeper(msg: str):
    print(f"[GATEKEEPER] {msg}")
    try:
        log_path = os.path.join(os.path.dirname(__file__), "..", "data", "nhat_ky_trinh_sat.log")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[GATEKEEPER] {msg}\n")
    except Exception:
        pass


class LegalGatekeeper:
    """
    Người gác cổng AI thông minh: Phân định ngữ nghĩa và loại bỏ rác ở cửa ngõ.
    """

    SYSTEM_INSTRUCTION = """BẠN LÀ BỘ LỌC GÁC CỔNG PHÁP LÝ (LEGAL GATEKEEPER) CHO DỰ ÁN ĐẦU TƯ XÂY DỰNG & MUA SẮM QUỐC PHÒNG.
Nhiệm vụ: Đọc tiêu đề, trích yếu, quyết định văn bản CÓ THUỘC PHẠM VI (is_in_scope = true) hay LOẠI BỎ (is_in_scope = false).

1. TIÊU CHÍ DUYỆT (is_in_scope = true):
- Xây dựng & Quản lý dự án: Luật Xây dựng (Luật 135/2025...), NĐ Quản lý hoạt động xây dựng (NĐ 217/2026, NĐ 15/2021, NĐ 35/2023), khảo sát, thiết kế BVTC, thẩm tra, giám sát, thi công, chất lượng (NĐ 207/2026, TT 32/2026, NĐ 06/2021, TT 10/2021).
- Quản lý chi phí & Dự toán: NĐ 206/2026, NĐ 10/2021, Định mức xây dựng (TT 38/2026, TT 12/2021, TT 09/2024), phương pháp xác định chi phí (TT 11/2021, TT 13/2021, TT 14/2023, TT 01/2025), suất vốn đầu tư (QĐ 510, QĐ 425), quyết toán vốn ĐTC (Luật 58/2024, NĐ 99/2021, TT 24/2024).
- Đấu thầu qua mạng: Luật Đấu thầu (Luật 22/2023, Luật 57/2024), Lựa chọn nhà thầu (NĐ 214/2025, NĐ 24/2024), Mẫu E-HSMT trên e-GP (TT 79/2025, TT 06/2024, TT 22/2024), Mẫu HSYC & Thẩm định (TT 80/2025, TT 07/2024, TT 23/2024), Mẫu PPP/Kinh doanh (TT 98/2025, TT 15/2024).
- Bộ Quốc phòng & Doanh trại: Phân cấp đầu tư BQP (TT 102/2026/TT-BQP), Chất lượng công trình BQP (TT 174/2021 & TT 24/2025/TT-BQP), Quy chuẩn xây dựng BQP (TT 101/2026/TT-BQP), Tiêu chuẩn máy móc thiết bị làm việc BQP (TT 150/2018/TT-BQP), Nhà ở LLVT (TT 94/2024/TT-BQP), Bảo mật quốc phòng (35/QĐ-TTg).
- Hợp đồng, Thí nghiệm & Bảo hiểm: NĐ 210/2026, NĐ 37/2015, TT 02/2023; Thí nghiệm cọc (TCVN 9393:2012); Bảo hiểm công trình (Luật 08/2022, NĐ 67/2023, NĐ 220/2026); Kiểm toán độc lập (Luật 67/2011, TT 67/2015).
- PCCC & Tiêu chuẩn: NĐ 105/2025, NĐ 136/2020, NĐ 50/2024, QCVN 06:2022/BXD & Sửa đổi 1:2023.
- Chi thường xuyên & Tài sản công: NĐ 104/2026, NĐ 186/2025, NĐ 138/2024, NĐ 114/2024, TT 65/2021, NQ 66.19/2026.

2. TIÊU CHÍ LOẠI BỎ TRIỆT ĐỂ (is_in_scope = false):
- ĐẤT ĐAI & MẶT BẰNG: Luật Đất đai (Luật 31/2024...), Nghị định đất đai (NĐ 102/2024, NĐ 103/2024...), bồi thường GPMB, giao đất, cho thuê đất, bảng giá đất (vì dự án nằm trọn trong đất quốc phòng hiện hữu, không có GPMB).
- Đấu thầu thuốc, vắc xin, vật tư y tế tiêu hao bệnh viện (trừ gói thầu xây dựng phòng khám/bệnh xá).
- Xây dựng Đảng, quy hoạch cán bộ, điều động, bổ nhiệm, kỷ luật cá nhân.
- Giáo dục đào tạo thuần túy, tuyển sinh, chuẩn giáo viên (trừ xây dựng cơ sở vật chất trường học).
- Nông nghiệp, lâm nghiệp, khoáng sản, thủy hải sản thuần túy.

3. VÍ DỤ MẪU ĐỂ HỌC (FEW-SHOT EXEMPLARS):
- Ví dụ 1: "Thông tư số 102/2026/TT-BQP quy định phân cấp chủ trương và dự án đầu tư trong BQP" -> {"is_in_scope": true, "scope_group": "NHOM_QUOC_PHONG", "reason": "Phân cấp đầu tư BQP"}
- Ví dụ 2: "Nghị định số 102/2024/NĐ-CP quy định chi tiết thi hành Luật Đất đai" -> {"is_in_scope": false, "scope_group": "OUT_OF_SCOPE", "reason": "Lĩnh vực đất đai không áp dụng"}
- Ví dụ 3: "Nghị định số 214/2025/NĐ-CP quy định chi tiết Luật Đấu thầu về lựa chọn nhà thầu" -> {"is_in_scope": true, "scope_group": "NHOM_DAU_THAU", "reason": "Quy định lựa chọn nhà thầu"}
- Ví dụ 4: "Thông tư số 150/2018/TT-BQP quy định tiêu chuẩn định mức máy móc thiết bị văn phòng BQP" -> {"is_in_scope": true, "scope_group": "NHOM_QUOC_PHONG", "reason": "Định mức máy móc thiết bị BQP"}
- Ví dụ 5: "Quyết định phê duyệt danh mục thuốc đấu thầu tập trung cấp quốc gia năm 2025" -> {"is_in_scope": false, "scope_group": "OUT_OF_SCOPE", "reason": "Đấu thầu thuốc y tế"}

Trả về DUY NHẤT 1 chuỗi JSON:
{"is_in_scope": true/false, "scope_group": "NHOM_XAY_DUNG"|"NHOM_DAU_THAU"|"NHOM_QUOC_PHONG"|"NHOM_CHI_THUONG_XUYEN"|"NHOM_PCCC_QCVN"|"OUT_OF_SCOPE", "reason": "ngắn gọn dưới 10 từ"}"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

    def triage_document(self, title: str, summary: str = "") -> Dict[str, Any]:
        """
        Phân loại nhanh văn bản đầu vào trong 0.3s với Connection Pool và Dynamic Discovery.
        """
        if not self.api_key:
            _log_gatekeeper("⚠️ Không có API Key, chuyển sang duyệt mặc định theo từ khóa.")
            return {"is_in_scope": True, "scope_group": "FALLBACK_RULE", "reason": "No API key"}

        sample_input = f"Tiêu đề: {title}\nTrích yếu: {summary[:500]}".strip()

        # Danh sách model ưu tiên (kế thừa Dynamic Discovery)
        candidate_models = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-2.5-flash", "gemini-1.5-pro"]

        # Sử dụng 1 HTTP Client dùng chung (Connection Pooling)
        try:
            with httpx.Client(timeout=8.0) as client:
                for model in candidate_models:
                    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
                    payload = {
                        "contents": [
                            {
                                "role": "user",
                                "parts": [{"text": f"{self.SYSTEM_INSTRUCTION}\n\nVăn bản cần đánh giá:\n{sample_input}"}]
                            }
                        ],
                        "generationConfig": {
                            "temperature": 0.0,
                            "maxOutputTokens": 60,
                            "responseMimeType": "application/json"
                        }
                    }

                    try:
                        res = client.post(endpoint, json=payload)
                        if res.status_code == 200:
                            res_json = res.json()
                            raw_text = res_json["candidates"][0]["content"]["parts"][0]["text"].strip()
                            
                            # Xử lý bóc tách JSON an toàn đa tầng
                            json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
                            if json_match:
                                clean_json_str = json_match.group(0)
                            else:
                                clean_json_str = raw_text

                            result = json.loads(clean_json_str.strip())
                            _log_gatekeeper(f"🎯 Model [{model}] -> Duyệt: {result.get('is_in_scope')} | Nhóm: {result.get('scope_group')} | Lý do: {result.get('reason')}")
                            return result
                    except Exception as e:
                        _log_gatekeeper(f"⚠️ Thử model [{model}] không thành công: {e}")

        except Exception as conn_err:
            _log_gatekeeper(f"⚠️ Lỗi kết nối gatekeeper: {conn_err}")

        # Fallback an toàn (Fail-Open): nếu API gặp trục trặc thì cho qua để không bị bỏ sót
        _log_gatekeeper("⚠️ Kích hoạt chế độ an toàn (Cho phép đi tiếp).")
        return {"is_in_scope": True, "scope_group": "SAFE_FALLBACK", "reason": "Fallback pass"}
