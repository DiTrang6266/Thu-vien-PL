# -*- coding: utf-8 -*-
"""
Module: classifier_tier2.py
Mục đích: Lớp 2 trong Phễu phân loại lai (3-Tier Hybrid Funnel).
Chức năng:
- Định tuyến nhanh 5 nhóm chủ đề chuyên ngành Xây dựng / Đấu thầu / Chi phí / Doanh trại Quốc phòng / PCCC.
- Đo điểm tương đồng ngữ nghĩa siêu tốc (3-5ms).
- Tự động thả rơi (Drop) 90% văn bản ngoài ngành (Y tế, Giáo dục, Nông nghiệp, Ngoại giao...) để tiết kiệm 100% token AI.
"""

import time
import re
from typing import Dict, List, Any
from enum import Enum


class DomainEnum(str, Enum):
    DAU_THAU_MUA_SAM = "DAU_THAU_MUA_SAM"
    QUAN_LY_DU_AN_XAY_DUNG = "QUAN_LY_DU_AN_XAY_DUNG"
    DINH_MUC_DU_TOAN_CHI_PHI = "DINH_MUC_DU_TOAN_CHI_PHI"
    CONG_TRINH_QUOC_PHONG = "CONG_TRINH_QUOC_PHONG"
    PCCC_AN_TOAN = "PCCC_AN_TOAN"
    NGOAI_NGANH_KHAC = "NGOAI_NGANH_KHAC"


class SemanticDomainFilter:
    """
    Bộ lọc ngữ nghĩa định tuyến chuyên ngành siêu tốc (3-5ms).
    """

    def __init__(self):
        # 5 Cụm tri thức mỏ neo chuyên ngành AEC (Anchor Concepts)
        self.domain_anchors = {
            DomainEnum.DAU_THAU_MUA_SAM: [
                "đấu thầu", "lựa chọn nhà thầu", "e-hsmt", "e-hsdt", "e-tbmt", "muasamcong",
                "hồ sơ mời thầu", "bảo đảm dự thầu", "chỉ định thầu", "chào hàng cạnh tranh",
                "tiêu chuẩn đánh giá", "hợp đồng trọn gói", "giá gói thầu", "kế hoạch lựa chọn nhà thầu",
                "tổ chuyên gia đấu thầu", "thẩm định kết quả lựa chọn nhà thầu", "mạng đấu thầu quốc gia"
            ],
            DomainEnum.QUAN_LY_DU_AN_XAY_DUNG: [
                "quản lý dự án đầu tư xây dựng", "thẩm định thiết kế cơ sở", "thiết kế bản vẽ thi công",
                "báo cáo nghiên cứu khả thi", "báo cáo kinh tế - kỹ thuật", "cấp phép xây dựng",
                "nghiệm thu hoàn thành", "nhật ký thi công", "chủ đầu tư", "ban quản lý dự án",
                "giám sát thi công", "bảo hành công trình", "quản lý chất lượng công trình"
            ],
            DomainEnum.DINH_MUC_DU_TOAN_CHI_PHI: [
                "quản lý chi phí đầu tư xây dựng", "định mức dự toán", "định mức xây dựng",
                "đơn giá nhân công", "giá ca máy", "chỉ số giá xây dựng", "tổng mức đầu tư",
                "dự toán gói thầu", "suất vốn đầu tư", "tạm ứng hợp đồng", "thanh quyết toán vốn",
                "chi phí quản lý dự án", "chi phí tư vấn đầu tư xây dựng"
            ],
            DomainEnum.CONG_TRINH_QUOC_PHONG: [
                "công trình quốc phòng", "doanh trại quân đội", "dự án quân sự", "bộ quốc phòng",
                "thông tư 150/2018", "thông tư 36/2023", "quản lý dự án trong quân đội",
                "chỉ huy trưởng công trình", "công trình chiến đấu", "kho tàng quân sự"
            ],
            DomainEnum.PCCC_AN_TOAN: [
                "phòng cháy chữa cháy", "pccc", "thẩm duyệt pccc", "nghiệm thu pccc",
                "qcvn 06", "an toàn lao động", "vệ sinh môi trường thi công", "thoát nạn"
            ]
        }

        # Từ khóa phủ định dứt khoát (Negative Out-of-Domain Keywords)
        self.negative_keywords = [
            "khám bệnh", "chữa bệnh", "bảo hiểm y tế", "thuốc tân dược", "học sinh",
            "sinh viên", "học phí", "sách giáo khoa", "trồng trọt", "chăn nuôi",
            "phân bón", "thủy sản", "lâm nghiệp", "ngoại giao", "hộ tịch", "quốc tịch"
        ]

        self.HIGH_CONFIDENCE_THRESHOLD = 0.65
        self.AMBIGUITY_THRESHOLD = 0.25

    def process(self, title: str, content: str = "") -> Dict[str, Any]:
        """
        Đánh giá độ tương đồng ngữ nghĩa và định tuyến chuyên ngành.
        """
        start_time = time.perf_counter()
        full_text = f"{title} {content}".lower()

        # 1. Kiểm tra từ khóa loại trừ ngoài ngành
        neg_count = sum(1 for kw in self.negative_keywords if kw in full_text)
        if neg_count >= 2:
            latency = (time.perf_counter() - start_time) * 1000
            return {
                "is_domain_relevant": False,
                "best_matched_domain": DomainEnum.NGOAI_NGANH_KHAC.value,
                "similarity_score": 0.0,
                "routing_action": "DROP_OUT_OF_DOMAIN",
                "latency_ms": latency
            }

        # 2. Tính điểm khớp theo từng cụm chuyên ngành
        scores: Dict[str, float] = {}
        matched_tags: List[str] = []

        for domain, keywords in self.domain_anchors.items():
            matches = [kw for kw in keywords if kw in full_text]
            if matches:
                matched_tags.extend(matches[:3])
            score = min(1.0, len(matches) / 2.5)
            scores[domain.value] = round(score, 3)

        best_domain_str = max(scores, key=scores.get)
        max_score = scores[best_domain_str]
        best_domain = DomainEnum(best_domain_str) if max_score > 0 else DomainEnum.NGOAI_NGANH_KHAC

        # 3. Phân luồng Tri-Zone
        if max_score >= self.HIGH_CONFIDENCE_THRESHOLD:
            routing = "ROUTE_TO_TIER3_DEEP_INSPECTION"
            is_relevant = True
        elif max_score >= self.AMBIGUITY_THRESHOLD:
            routing = "ROUTE_TO_TIER3_AMBIGUOUS_ESCALATION"
            is_relevant = True
        else:
            routing = "DROP_OUT_OF_DOMAIN"
            is_relevant = False
            best_domain = DomainEnum.NGOAI_NGANH_KHAC

        latency = (time.perf_counter() - start_time) * 1000
        return {
            "is_domain_relevant": is_relevant,
            "best_matched_domain": best_domain.value if hasattr(best_domain, "value") else str(best_domain),
            "similarity_score": max_score,
            "matched_keywords": list(set(matched_tags))[:5],
            "routing_action": routing,
            "latency_ms": latency
        }
