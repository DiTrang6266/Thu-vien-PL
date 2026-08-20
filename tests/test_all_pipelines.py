# -*- coding: utf-8 -*-
"""
Bộ kiểm thử tự động toàn trình (Comprehensive Test Suite):
1. Test Lớp 1: Bóc tách Thể thức & Thẩm quyền (classifier_tier1)
2. Test Lớp 2: Bộ lọc Ngữ nghĩa Chuyên ngành (classifier_tier2)
3. Test Lớp 3: Bộ não AI Gemini & Pydantic Schema (ai_analyzer)
4. Test Động cơ Đồng bộ Sổ cái Excel (excel_sync_engine)
5. Test Động cơ Ốp Căn cứ Word theo Thứ bậc Lập pháp (word_grounding_engine)
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.classifier_tier1 import StructuralAuthorityMatcher, DocumentType
from modules.classifier_tier2 import SemanticDomainFilter, DomainEnum
from modules.ai_analyzer import LegalAIAnalyzer
from modules.excel_sync_engine import LegalExcelSyncEngine
from modules.word_grounding_engine import get_active_legal_bases


class TestHybridPipeline(unittest.TestCase):

    def setUp(self):
        self.tier1 = StructuralAuthorityMatcher()
        self.tier2 = SemanticDomainFilter()
        self.ai = LegalAIAnalyzer()

    def test_tier1_valid_decree(self):
        title = "Nghị định số 24/2024/NĐ-CP quy định chi tiết một số điều của Luật Đấu thầu"
        res = self.tier1.process(title)
        self.assertTrue(res["is_valid_legal_doc"])
        self.assertEqual(res["doc_type"], DocumentType.NGHI_DINH.value)
        self.assertEqual(res["authority"], "GOV")

    def test_tier1_valid_circular(self):
        title = "Thông tư số 06/2024/TT-BKHĐT hướng dẫn mẫu E-HSMT trên Hệ thống mạng đấu thầu quốc gia"
        res = self.tier1.process(title)
        self.assertTrue(res["is_valid_legal_doc"])
        self.assertEqual(res["doc_type"], DocumentType.THONG_TU.value)
        self.assertEqual(res["authority"], "BKHDT")

    def test_tier1_junk_rejection(self):
        title = "Thông báo số 12/TB-VP về việc phân công lịch trực Tết Nguyên đán 2026"
        res = self.tier1.process(title)
        self.assertFalse(res["is_valid_legal_doc"])
        self.assertIn("JUNK_ADMINISTRATIVE_NOTICE", res["rejection_reason"])

    def test_tier2_domain_matching(self):
        title = "Thông tư hướng dẫn xác định định mức dự toán và đơn giá nhân công xây dựng"
        res = self.tier2.process(title)
        self.assertTrue(res["is_domain_relevant"])
        self.assertEqual(res["best_matched_domain"], DomainEnum.DINH_MUC_DU_TOAN_CHI_PHI.value)

    def test_tier2_out_of_domain_drop(self):
        title = "Thông tư quy định mức giá thanh toán khám bệnh chữa bệnh bảo hiểm y tế và thuốc tân dược"
        res = self.tier2.process(title)
        self.assertFalse(res["is_domain_relevant"])
        self.assertEqual(res["routing_action"], "DROP_OUT_OF_DOMAIN")

    def test_excel_sync_and_word_grounding(self):
        excel_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Kho_Can_Cu_Phap_Ly.xlsx"))
        sync_engine = LegalExcelSyncEngine(excel_path)

        # Giả lập ban hành Thông tư mới thay thế Thông tư 11/2021
        res = sync_engine.sync_new_document(
            so_hieu="99/2026/TT-BXD",
            loai_vb="Thông tư",
            co_quan="Bộ Xây dựng",
            ngay_bh="20/08/2026",
            ngay_hl="20/08/2026",
            linh_vuc="Quản lý chi phí",
            cau_can_cu="Căn cứ Thông tư số 99/2026/TT-BXD ngày 20 tháng 8 năm 2026 của Bộ trưởng Bộ Xây dựng;",
            thay_the_cho=["11/2021/TT-BXD"],
            tags_bo_sung=["DU_TOAN", "QUAN_LY_CHI_PHI", "XD-01"],
            thu_bac=300
        )
        self.assertTrue(res["success"])

        # Kiểm tra trích xuất căn cứ cho Tờ trình Dự toán
        bases = get_active_legal_bases(
            dossier_type="TO_TRINH_DU_TOAN",
            package_code="XD-01",
            excel_path=excel_path
        )
        self.assertTrue(len(bases) > 0)
        
        # Kiểm tra thứ bậc: Luật (100) phải đứng trước Nghị định (200), Thông tư (300)
        ranks = [b["thu_bac"] for b in bases]
        self.assertEqual(ranks, sorted(ranks))
        
        # Đảm bảo văn bản hết hạn 63/2014 không xuất hiện
        so_hieus = [b["so_hieu"] for b in bases]
        self.assertNotIn("63/2014/NĐ-CP", so_hieus)


if __name__ == "__main__":
    unittest.main()
