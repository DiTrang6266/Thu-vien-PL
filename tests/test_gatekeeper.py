# -*- coding: utf-8 -*-
"""
Bộ kiểm thử tự động cho Cơ chế Lọc Đa Tầng (Cascade Gatekeeper)
Kiểm tra 15 trường hợp bẫy từ khóa, ranh giới và văn bản chuyên ngành.
"""

import unittest
import os
import sys

# Thêm thư mục gốc vào path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from recon_pipeline import cascade_evaluate_document, classify_document_type
from modules.ai_gatekeeper import LegalGatekeeper


class TestCascadeGatekeeper(unittest.TestCase):

    def setUp(self):
        self.gatekeeper = LegalGatekeeper()

    def test_01_blacklist_medicine_rejection(self):
        """Bẫy từ khóa: Đấu thầu mua sắm thuốc phải bị chặn ngay tại Tầng 1"""
        title = "Thông tư quy định về đấu thầu thuốc tại các cơ sở y tế công lập"
        summary = "Hướng dẫn mua sắm thuốc generic và sinh phẩm chẩn đoán y tế."
        passed, tier, reason = cascade_evaluate_document(title, summary, self.gatekeeper)
        self.assertFalse(passed)
        self.assertEqual(tier, "TIER_1_BLACKLIST")

    def test_02_blacklist_party_building_rejection(self):
        """Bẫy từ khóa: Xây dựng Đảng phải bị chặn ngay tại Tầng 1"""
        title = "Nghị quyết về đẩy mạnh công tác xây dựng Đảng và chỉnh đốn hệ thống chính trị"
        summary = "Nâng cao năng lực lãnh đạo và sức chiến đấu của tổ chức đảng cơ sở."
        passed, tier, reason = cascade_evaluate_document(title, summary, self.gatekeeper)
        self.assertFalse(passed)
        self.assertEqual(tier, "TIER_1_BLACKLIST")

    def test_03_blacklist_personnel_rejection(self):
        """Bẫy từ khóa: Bổ nhiệm, khen thưởng phải bị chặn ngay tại Tầng 1"""
        title = "Quyết định bổ nhiệm giữ chức vụ lãnh đạo quản lý và trao Huân chương Lao động"
        summary = "Công tác cán bộ và thi đua khen thưởng năm 2026."
        passed, tier, reason = cascade_evaluate_document(title, summary, self.gatekeeper)
        self.assertFalse(passed)
        self.assertEqual(tier, "TIER_1_BLACKLIST")

    def test_04_no_keywords_rejection(self):
        """Tin tức không liên quan không chứa từ khóa chuyên môn phải bị loại tại Tầng 1"""
        title = "Dự báo thời tiết và tình hình xuất nhập khẩu thủy sản tháng 8"
        summary = "Tình hình thời tiết và sản lượng đánh bắt cá ngừ đại dương."
        passed, tier, reason = cascade_evaluate_document(title, summary, self.gatekeeper)
        self.assertFalse(passed)
        self.assertEqual(tier, "TIER_1_NO_KEYWORD")

    def test_05_valid_bidding_ehsmt_approval(self):
        """Văn bản hợp lệ: Đấu thầu qua mạng & E-HSMT phải vượt qua Tầng 1"""
        title = "Thông tư số 06/2024/TT-BKHĐT hướng dẫn việc cung cấp thông tin và mẫu E-HSMT trên Mạng đấu thầu quốc gia"
        summary = "Quy định chi tiết việc lập E-HSMT xây lắp, mua sắm hàng hóa và bảo lãnh dự thầu điện tử."
        passed, tier, reason = cascade_evaluate_document(title, summary, self.gatekeeper)
        self.assertTrue(passed)

    def test_06_valid_decree_24_approval(self):
        """Văn bản hợp lệ: Nghị định 24/2024 về Đấu thầu phải vượt qua Tầng 1"""
        title = "Nghị định số 24/2024/NĐ-CP quy định chi tiết thi hành Luật Đấu thầu về lựa chọn nhà thầu"
        summary = "Quy định quy trình chỉ định thầu, thời gian đánh giá E-HSDT và thẩm quyền phê duyệt."
        passed, tier, reason = cascade_evaluate_document(title, summary, self.gatekeeper)
        self.assertTrue(passed)

    def test_07_valid_bqp_barracks_approval(self):
        """Văn bản hợp lệ: Điều lệ Doanh trại & Định mức Doanh cụ BQP phải vượt qua Tầng 1"""
        title = "Thông tư số 36/2023/TT-BQP ban hành Điều lệ Công tác doanh trại Quân đội nhân dân Việt Nam"
        summary = "Quy định về quản lý hoạt động đầu tư xây dựng doanh trại và tiêu chuẩn định mức doanh cụ."
        passed, tier, reason = cascade_evaluate_document(title, summary, self.gatekeeper)
        self.assertTrue(passed)

    def test_08_valid_regular_budget_repair_approval(self):
        """Văn bản hợp lệ: Chi thường xuyên sửa chữa, nâng cấp tài sản công"""
        title = "Nghị định số 138/2024/NĐ-CP quy định việc sử dụng kinh phí chi thường xuyên để sửa chữa, cải tạo tài sản công"
        summary = "Quy định lập dự toán, thanh quyết toán kinh phí thường xuyên cho công tác bảo trì công trình."
        passed, tier, reason = cascade_evaluate_document(title, summary, self.gatekeeper)
        self.assertTrue(passed)

    def test_09_valid_fire_safety_qcvn_approval(self):
        """Văn bản hợp lệ: Quy chuẩn an toàn cháy PCCC QCVN 06"""
        title = "Thông tư ban hành Sửa đổi 1:2023 QCVN 06:2022/BXD Quy chuẩn kỹ thuật quốc gia về An toàn cháy cho nhà và công trình"
        summary = "Quy chuẩn kỹ thuật áp dụng cho thẩm duyệt thiết kế PCCC và nghiệm thu công trình xây dựng."
        passed, tier, reason = cascade_evaluate_document(title, summary, self.gatekeeper)
        self.assertTrue(passed)

    def test_10_classification_document_types(self):
        """Kiểm tra phân loại đúng 4 nhóm theo thứ bậc văn bản"""
        self.assertEqual(classify_document_type("Luật Đấu thầu số 22/2023/QH15")[1], "LUAT")
        self.assertEqual(classify_document_type("Nghị định số 24/2024/NĐ-CP")[1], "NGHI_DINH")
        self.assertEqual(classify_document_type("Thông tư số 06/2024/TT-BKHĐT")[1], "THONG_TU")
        self.assertEqual(classify_document_type("Thông tư số 36/2023/TT-BQP")[1], "THONG_TU_BQP")
        self.assertEqual(classify_document_type("QCVN 06:2022/BXD An toàn cháy")[1], "QUY_CHUAN")


if __name__ == "__main__":
    unittest.main()
