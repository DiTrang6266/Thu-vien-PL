# -*- coding: utf-8 -*-
"""
Module: classifier_tier2.py
Mục đích: Lớp 2 trong Phễu phân loại lai (3-Tier Hybrid Funnel) - Sàng lọc Thể thức & Chuyên môn siêu tốc (Latency < 0.1ms).
Nhiệm vụ:
1. Nhận diện và loại bỏ dứt khoát 100% Văn bản cá biệt (giao vốn, phân bổ dự toán, bổ nhiệm, khen thưởng, thu hồi đất...).
2. Nhận diện và loại bỏ dứt khoát 100% Văn bản ngành ngoài (hoa tiêu hàng hải, bến thủy nội địa, luồng tàu, sát hạch lái xe, y tế điều trị, giáo dục mầm non...).
3. Nhận diện và loại bỏ dứt khoát Văn bản đặc thù cho 1 dự án riêng (đường sắt Lào Cai, sân bay Long Thành, metro riêng...).
4. Phân loại chuẩn xác vào 4 Trụ cột Chuyên môn Cốt lõi:
   - Trụ cột 1: DAU_TU_CONG_XAY_DUNG
   - Trụ cột 2: DAU_THAU_MUA_SAM
   - Trụ cột 3: CHI_THUONG_XUYEN_TSCONG
   - Trụ cột 4: QUOC_PHONG_PCCC
"""

import re
import logging
from enum import Enum
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class DomainEnum(str, Enum):
    DAU_TU_CONG_XAY_DUNG = "DAU_TU_CONG_XAY_DUNG"
    DAU_THAU_MUA_SAM = "DAU_THAU_MUA_SAM"
    CHI_THUONG_XUYEN_TSCONG = "CHI_THUONG_XUYEN_TSCONG"
    QUOC_PHONG_PCCC = "QUOC_PHONG_PCCC"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"


class HybridTier2Classifier:
    """
    Bộ lọc Gác cổng Lớp 2 (Rule-based & Regex Heuristics).
    Tốc độ: < 0.1 mili-giây / văn bản. Chi phí: 0 đồng, 0 token.
    """

    STRICT_OUT_OF_SCOPE_BLACKLIST = [
        "hoa tiêu", "luồng hàng hải", "bến thủy nội địa", "khu neo đậu", "cảng biển",
        "trục vớt cứu hộ", "đăng kiểm tàu cá", "phương tiện thủy nội địa", "thuyền viên",
        "bằng thuyền trưởng", "bằng máy trưởng", "hoa tiêu hàng hải", "hoa tiêu đường thủy",
        "sát hạch lái xe", "giấy phép lái xe", "bằng lái xe", "đăng kiểm xe cơ giới",
        "phù hiệu xe", "trạm thu phí bot", "tải trọng trục xe", "vận tải hành khách tuyến cố định",
        "xe buýt", "taxi", "niên hạn sử dụng xe",
        "bảo vệ thực vật", "thú y", "tiêm phòng dịch", "trồng rừng thay thế", "cấp bù giá thủy lợi",
        "giống cây trồng", "giống vật nuôi", "kiểm dịch động vật",
        "danh mục thuốc bảo hiểm y tế", "phác đồ điều trị", "khám chữa bệnh", "chứng chỉ hành nghề y",
        "khung chương trình giáo dục", "chuẩn đầu ra đại học", "học phí mầm non", "sách giáo khoa",
        "thuế thu nhập cá nhân", "bảo hiểm thất nghiệp", "mức lương tối thiểu vùng", "chế độ thai sản",
        "hộ tịch", "chứng thực chữ ký", "trợ cấp xã hội",
        "thi hành án dân sự", "giám định tư pháp hình sự", "thủ tục tố tụng", "trọng tài thương mại vụ việc"
    ]

    REJECT_INDIVIDUAL_PATTERNS = [
        r"(?:phê duyệt|chấp thuận)\s+(?:chủ trương đầu tư|dự án|báo cáo NCKT|kế hoạch lựa chọn nhà thầu|kết quả lựa chọn nhà thầu|thiết kế bản vẽ|dự toán).+?(?:tại|thuộc|của|tỉnh|huyện|thành phố|ban quản lý|công ty)",
        r"(?:giao|điều chỉnh|bổ sung|phân bổ|kéo dài thời gian thực hiện)\s+(?:kế hoạch vốn|dự toán|dự toán chi|dự toán ngân sách|chi tiết vốn|ngân sách).*?(?:cho|năm 20\d\d|đợt \d+)",
        r"(?:bổ nhiệm|miễn nhiệm|điều động|luân chuyển|khen thưởng|kỷ luật|cử đi công tác|nghỉ hưu|thành lập hội đồng|thành lập ban chỉ đạo)",
        r"(?:thu hồi đất|giao đất|cho thuê đất|chuyển mục đích sử dụng đất).+?(?:để thực hiện dự án|cho công ty|tại xã|tại phường)",
        r"(?:xếp hạng doanh nghiệp|công nhận kết quả|chỉ định đơn vị|ủy quyền thực hiện)",
        r"(?:v/v|về việc)\s+(?:giao|phân bổ|điều chỉnh)\s+(?:dự toán|kế hoạch vốn|ngân sách).+?cho"
    ]

    PROJECT_SPECIFIC_PATTERNS = [
        r"dự án thành phần \d+",
        r"tuyến đường sắt lào cai\s*-\s*hà nội\s*-\s*hải phòng",
        r"sân bay long thành",
        r"cảng hàng không quốc tế long thành",
        r"đường bộ cao tốc bắc\s*-\s*nam",
        r"tuyến metro số \d+",
        r"đường sắt đô thị tuyến số \d+",
        r"cầu vượt sông \w+",
        r"nhà máy nhiệt điện \w+",
        r"nhà máy thủy điện \w+",
        r"khu tái định cư \w+"
    ]

    DOMAIN_ANCHORS = {
        DomainEnum.DAU_TU_CONG_XAY_DUNG: [
            "đầu tư công", "luật xây dựng", "quản lý dự án", "quản lý dự án đầu tư", "chi phí đầu tư xây dựng",
            "dự toán xây dựng", "định mức xây dựng", "định mức dự toán", "tổng mức đầu tư", "chủ trương đầu tư",
            "quy chuẩn kỹ thuật quốc gia", "qcvn", "tiêu chuẩn quốc gia", "tcvn", "thẩm định thiết kế",
            "nghiệm thu công trình", "quản lý chất lượng công trình", "bảo trì công trình", "phân cấp công trình",
            "hợp đồng xây dựng", "giám sát thi công", "khảo sát xây dựng", "quy hoạch đô thị", "quy hoạch nông thôn",
            "quy hoạch xây dựng", "chỉ số giá xây dựng", "suất vốn đầu tư", "giá ca máy", "đơn giá nhân công xây dựng"
        ],
        DomainEnum.DAU_THAU_MUA_SAM: [
            "đấu thầu", "luật đấu thầu", "lựa chọn nhà thầu", "hồ sơ mời thầu", "e-hsmt", "e-hsyc",
            "hồ sơ dự thầu", "e-hsdt", "kế hoạch lựa chọn nhà thầu", "khlcnt", "đấu thầu qua mạng",
            "mạng đấu thầu quốc gia", "vneps", "chỉ định thầu", "chào hàng cạnh tranh", "bảo đảm dự thầu",
            "bảo lãnh tạm ứng", "hợp đồng trọn gói", "hợp đồng theo đơn giá", "tổ chuyên gia", "tổ thẩm định"
        ],
        DomainEnum.CHI_THUONG_XUYEN_TSCONG: [
            "tài sản công", "quản lý tài sản công", "luật quản lý, sử dụng tài sản công",
            "chi thường xuyên", "kinh phí chi thường xuyên", "vốn sự nghiệp",
            "sửa chữa tài sản công", "bảo dưỡng tài sản công", "cải tạo công trình",
            "nâng cấp công trình", "mua sắm tài sản công", "mua sắm tập trung",
            "tiêu chuẩn định mức máy móc", "tiêu chuẩn định mức xe ô tô", "thuê tài sản công",
            "thanh lý tài sản công", "tiêu chuẩn định mức sử dụng trụ sở"
        ],
        DomainEnum.QUOC_PHONG_PCCC: [
            "quốc phòng", "công trình quốc phòng", "doanh trại", "doanh trại quân đội",
            "bộ quốc phòng", "quân khu", "công trình chiến đấu", "khu quân sự",
            "pccc", "phòng cháy", "chữa cháy", "an toàn cháy", "qcvn 06", "thẩm duyệt pccc", "nghiệm thu pccc"
        ]
    }

    def classify_and_filter(
        self,
        title: str,
        content_preview: str = "",
        doc_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        combined_text = f"{title} {content_preview}".lower()

        # Bước 1: Kiểm tra Danh mục Ngành ngoài dứt khoát
        for black_word in self.STRICT_OUT_OF_SCOPE_BLACKLIST:
            if re.search(r"\b" + re.escape(black_word) + r"\b", combined_text, re.IGNORECASE):
                return {
                    "is_accepted": False,
                    "target_domain": DomainEnum.OUT_OF_SCOPE,
                    "decision": "DROP_OUT_OF_SCOPE_INDUSTRY",
                    "reason": f"Thuộc danh mục ngành ngoài loại trừ ({black_word})."
                }

        # Bước 2: Kiểm tra Văn bản Cá biệt / Phân bổ vốn địa phương
        for pattern in self.REJECT_INDIVIDUAL_PATTERNS:
            if re.search(pattern, title, re.IGNORECASE):
                return {
                    "is_accepted": False,
                    "target_domain": DomainEnum.OUT_OF_SCOPE,
                    "decision": "DROP_INDIVIDUAL_DECISION",
                    "reason": "Quyết định cá biệt / phân bổ vốn / giao dự toán riêng cho 1 đối tượng cụ thể."
                }

        # Bước 3: Kiểm tra Văn bản Đặc thù cho 1 Dự án riêng biệt
        for p_pattern in self.PROJECT_SPECIFIC_PATTERNS:
            if re.search(p_pattern, title, re.IGNORECASE):
                return {
                    "is_accepted": False,
                    "target_domain": DomainEnum.OUT_OF_SCOPE,
                    "decision": "DROP_PROJECT_SPECIFIC_DOC",
                    "reason": "Văn bản ban hành định mức / quy chế đặc thù áp dụng riêng cho 1 dự án cá biệt."
                }

        # Bước 4: Tính điểm khớp với 4 Trụ cột Chuyên môn
        domain_scores = {
            DomainEnum.DAU_TU_CONG_XAY_DUNG: 0,
            DomainEnum.DAU_THAU_MUA_SAM: 0,
            DomainEnum.CHI_THUONG_XUYEN_TSCONG: 0,
            DomainEnum.QUOC_PHONG_PCCC: 0
        }

        for domain, keywords in self.DOMAIN_ANCHORS.items():
            for kw in keywords:
                if kw in combined_text:
                    domain_scores[domain] += 1

        best_domain = max(domain_scores, key=domain_scores.get)
        max_score = domain_scores[best_domain]

        meta = doc_metadata or {}
        authority = meta.get("authority", "").lower()
        is_gov_normative = any(org in authority for org in ["bộ xây dựng", "bộ kế hoạch", "bộ tài chính", "bộ quốc phòng", "chính phủ", "thủ tướng"])
        
        if max_score > 0 or is_gov_normative:
            return {
                "is_accepted": True,
                "target_domain": best_domain if max_score > 0 else DomainEnum.DAU_TU_CONG_XAY_DUNG,
                "decision": "ROUTE_TO_TIER3_AI_GATEKEEPER",
                "match_score": max_score,
                "reason": f"Phù hợp sơ bộ trụ cột {best_domain}, chuyển sang Lớp 3 AI thẩm định chuyên sâu."
            }

        return {
            "is_accepted": False,
            "target_domain": DomainEnum.OUT_OF_SCOPE,
            "decision": "DROP_NO_DOMAIN_MATCH",
            "reason": "Không chứa từ khóa hoặc tín hiệu nghiệp vụ thuộc 4 Trụ cột chuyên môn mục tiêu."
        }
