# -*- coding: utf-8 -*-
"""
Bộ kiểm thử tự động toàn diện: Phễu gác cổng 2 tầng và Động cơ Tham mưu Thực chiến.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.classifier_tier2 import HybridTier2Classifier, DomainEnum
from modules.ai_analyzer import LegalAIAnalyzer


def test_tier2_rejects_waterway_piloting():
    classifier = HybridTier2Classifier()
    title = "Văn bản hợp nhất Thông tư quy định về quản lý nhà nước chuyên ngành tại cảng thủy nội địa, bến thủy nội địa, khu neo đậu và quản lý hoạt động hoa tiêu đường thủy nội địa"
    res = classifier.classify_and_filter(title)
    assert res["is_accepted"] is False
    assert res["decision"] == "DROP_OUT_OF_SCOPE_INDUSTRY"


def test_tier2_rejects_macro_spatial_planning():
    """Quy hoạch tổng thể quốc gia vĩ mô ngoài ngành phải bị loại trừ dứt khoát."""
    classifier = HybridTier2Classifier()
    title = "Nghị quyết số 81/2023/QH15 về Quy hoạch tổng thể quốc gia thời kỳ 2021 - 2030, tầm nhìn đến năm 2050"
    res = classifier.classify_and_filter(title)
    assert res["is_accepted"] is False
    assert res["decision"] == "DROP_OUT_OF_SCOPE_INDUSTRY"


def test_tier2_rejects_project_specific_lao_cai():
    classifier = HybridTier2Classifier()
    title = "Thông tư ban hành định mức dự toán xây dựng Dự án thành phần 2 thuộc Dự án đầu tư xây dựng tuyến đường sắt Lào Cai - Hà Nội - Hải Phòng"
    res = classifier.classify_and_filter(title)
    assert res["is_accepted"] is False
    assert res["decision"] == "DROP_PROJECT_SPECIFIC_DOC"


def test_tier2_rejects_individual_allocation():
    classifier = HybridTier2Classifier()
    title = "Quyết định về việc phân bổ dự toán chi ngân sách nhà nước năm 2026 cho Ban Quản lý dự án 7"
    res = classifier.classify_and_filter(title)
    assert res["is_accepted"] is False
    assert res["decision"] == "DROP_INDIVIDUAL_DECISION"


def test_tier2_accepts_cost_management():
    classifier = HybridTier2Classifier()
    title = "Thông tư hướng dẫn xác định và quản lý chi phí đầu tư xây dựng, định mức dự toán xây dựng công trình"
    res = classifier.classify_and_filter(title)
    assert res["is_accepted"] is True
    assert res["target_domain"] == DomainEnum.DAU_TU_CONG_XAY_DUNG


def test_tier2_accepts_bidding_guideline():
    classifier = HybridTier2Classifier()
    title = "Thông tư hướng dẫn lập hồ sơ mời thầu xây lắp qua mạng"
    res = classifier.classify_and_filter(title)
    assert res["is_accepted"] is True
    assert res["target_domain"] == DomainEnum.DAU_THAU_MUA_SAM


def test_tier2_accepts_regular_expenditure():
    classifier = HybridTier2Classifier()
    title = "Thông tư quy định quản lý, sử dụng kinh phí chi thường xuyên để sửa chữa, bảo dưỡng tài sản công theo Nghị định 138/2024/NĐ-CP"
    res = classifier.classify_and_filter(title)
    assert res["is_accepted"] is True
    assert res["target_domain"] == DomainEnum.CHI_THUONG_XUYEN_TSCONG


def test_ai_nd30_citation_generation():
    analyzer = LegalAIAnalyzer()
    citation = analyzer.generate_nd30_citation(
        "Thông tư quy định chi tiết về quản lý chi phí đầu tư xây dựng",
        {"doc_number": "11/2021/TT-BXD", "authority": "Bộ Xây dựng", "ngay_ban_hanh": "31/08/2021"}
    )
    assert "Căn cứ Thông tư số 11/2021/TT-BXD" in citation
    assert "của Bộ trưởng Bộ Xây dựng" in citation
    assert citation.endswith(";")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
