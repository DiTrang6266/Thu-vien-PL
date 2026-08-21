# -*- coding: utf-8 -*-
"""
Unit test kiểm thử động cơ đúc Word (word_grounding_engine) và Trình sinh Web Card (web_card_generator).
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.word_grounding_engine import get_active_legal_bases, _get_legal_rank
from modules.web_card_generator import generate_mobile_card_web


class TestWordGroundingAndWebCards(unittest.TestCase):

    def test_01_legal_rank_hierarchy(self):
        """Kiểm tra thứ bậc lập pháp chuẩn Luật Ban hành VBQPPL."""
        self.assertEqual(_get_legal_rank("Luật"), 100)
        self.assertEqual(_get_legal_rank("Nghị quyết Quốc hội"), 100)
        self.assertEqual(_get_legal_rank("Nghị định"), 200)
        self.assertEqual(_get_legal_rank("Thông tư"), 300)
        self.assertEqual(_get_legal_rank("Quy chuẩn kỹ thuật"), 400)
        self.assertEqual(_get_legal_rank("Quyết định"), 400)

    def test_02_word_grounding_11_packages_coverage(self):
        """Kiểm tra trích xuất căn cứ pháp lý cho toàn bộ 11 gói thầu dự án."""
        packages = ["TV-01", "TV-02", "TV-03", "TV-04", "TV-05", "TV-06", "TV-07", "TV-08", "TV-09", "PTV-01", "XD-01"]
        for pkg in packages:
            bases = get_active_legal_bases(
                dossier_type="TO_TRINH_DU_TOAN",
                package_code=pkg,
                project_context={"is_bqp_project": True}
            )
            self.assertGreater(len(bases), 10, f"Gói thầu {pkg} phải trích xuất được nhiều hơn 10 căn cứ")
            
            # Kiểm tra 100% không chứa văn bản hết hiệu lực
            for b in bases:
                self.assertNotIn("hết hiệu lực", b["trang_thai"].lower(), f"Căn cứ {b['so_hieu']} bị hết hiệu lực nhưng vẫn lọt vào")
                self.assertNotIn("🔴", b["trang_thai"], f"Căn cứ {b['so_hieu']} có icon 🔴")

            # Kiểm tra thứ bậc lập pháp tăng dần
            ranks = [b["thu_bac"] for b in bases]
            self.assertTrue(all(ranks[i] <= ranks[i+1] for i in range(len(ranks)-1)), f"Thứ bậc lập pháp gói {pkg} chưa được sắp xếp tăng dần")

    def test_03_web_card_generation(self):
        """Kiểm tra sinh giao diện Web Card Di Động."""
        output_html = generate_mobile_card_web()
        self.assertTrue(os.path.exists(output_html))
        self.assertTrue(os.path.exists("docs/index.html"))
        self.assertTrue(os.path.exists("index.html"))

        with open(output_html, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("RAW_DATA = [", content)
        self.assertIn("copyClause", content)
        self.assertIn("toast", content)
        self.assertIn("🏛️ KHO CĂN CỨ PHÁP LÝ", content)


if __name__ == "__main__":
    unittest.main()
