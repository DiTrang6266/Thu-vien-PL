# -*- coding: utf-8 -*-
"""
Module: classifier_tier2.py
Mục đích: Lớp 2 trong Phễu phân loại lai (3-Tier Hybrid Funnel).
Nâng cấp: Siết chặt tiêu chí chuyên ngành Xây dựng, Đấu thầu, Dự toán, Quốc phòng, PCCC.
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
    def __init__(self):
        self.domain_anchors = {
            DomainEnum.DAU_THAU_MUA_SAM: [
                "đấu thầu", "lựa chọn nhà thầu", "e-hsmt", "e-hsdt", "e-tbmt", "muasamcong",
                "hồ sơ mời thầu", "chỉ định thầu", "chào hàng cạnh tranh", "kế hoạch lựa chọn nhà thầu",
                "luật đấu thầu", "mạng đấu thầu quốc gia", "tổ chuyên gia đấu thầu"
            ],
            DomainEnum.QUAN_LY_DU_AN_XAY_DUNG: [
                "quản lý dự án đầu tư xây dựng", "thẩm định thiết kế", "bản vẽ thi công",
                "nghiệm thu công trình", "giám sát thi công", "báo cáo nghiên cứu khả thi",
                "báo cáo kinh tế - kỹ thuật", "chất lượng công trình xây dựng", "giấy phép xây dựng",
                "quy hoạch đô thị", "quy hoạch xây dựng", "bảo trì công trình"
            ],
            DomainEnum.DINH_MUC_DU_TOAN_CHI_PHI: [
                "định mức dự toán", "định mức xây dựng", "quản lý chi phí đầu tư xây dựng",
                "đơn giá nhân công", "giá ca máy", "tổng mức đầu tư", "dự toán xây dựng",
                "suất vốn đầu tư", "chỉ số giá xây dựng"
            ],
            DomainEnum.CONG_TRINH_QUOC_PHONG: [
                "công trình quốc phòng", "doanh trại", "quân sự", "bộ quốc phòng",
                "dự án trong quân đội", "công trình chiến đấu"
            ],
            DomainEnum.PCCC_AN_TOAN: [
                "phòng cháy", "chữa cháy", "pccc", "thẩm duyệt pccc", "qcvn 06", "an toàn lao động xây dựng"
            ]
        }

        # Danh mục từ khóa phủ định dứt khoát
        self.negative_keywords = [
            "ngân hàng nhà nước", "tín dụng", "tiền tệ", "lãi suất", "thanh tra ngân hàng",
            "bảo hiểm y tế", "khám bệnh", "chữa bệnh", "thuốc tân dược", "học sinh",
            "sinh viên", "học phí", "sách giáo khoa", "trồng trọt", "chăn nuôi",
            "thủy sản", "hộ tịch", "quốc tịch", "ngoại giao", "hải quan", "thuế thu nhập cá nhân"
        ]

    def process(self, title: str, content: str = "") -> Dict[str, Any]:
        start_time = time.perf_counter()
        full_text = f"{title} {content}".lower()

        # 1. Chặn dứt khoát nếu chứa từ khóa ngoài ngành
        for neg in self.negative_keywords:
            if neg in full_text:
                latency = (time.perf_counter() - start_time) * 1000
                return {
                    "is_domain_relevant": False,
                    "best_matched_domain": DomainEnum.NGOAI_NGANH_KHAC.value,
                    "similarity_score": 0.0,
                    "routing_action": "DROP_OUT_OF_DOMAIN",
                    "latency_ms": latency
                }

        # 2. Tính điểm khớp theo từng nhóm
        scores: Dict[str, float] = {}
        for domain, keywords in self.domain_anchors.items():
            matches = [kw for kw in keywords if kw in full_text]
            score = len(matches)
            scores[domain.value] = score

        best_domain_str = max(scores, key=scores.get)
        max_score = scores[best_domain_str]

        if max_score >= 1:
            best_domain = DomainEnum(best_domain_str)
            is_relevant = True
            routing = "ROUTE_TO_TIER3_DEEP_INSPECTION"
        else:
            best_domain = DomainEnum.NGOAI_NGANH_KHAC
            is_relevant = False
            routing = "DROP_OUT_OF_DOMAIN"

        latency = (time.perf_counter() - start_time) * 1000
        return {
            "is_domain_relevant": is_relevant,
            "best_matched_domain": best_domain.value if hasattr(best_domain, "value") else str(best_domain),
            "similarity_score": float(max_score),
            "routing_action": routing,
            "latency_ms": latency
        }
