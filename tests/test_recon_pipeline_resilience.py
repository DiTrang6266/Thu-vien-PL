# -*- coding: utf-8 -*-
"""
Unit test kiểm thử độ bền vững (Resilience) của Pipeline Trinh sát Pháp lý recon_pipeline.py.
"""

import os
import sys
import json
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import recon_pipeline
from recon_pipeline import (
    safe_html,
    load_known_documents,
    save_known_documents,
    format_compact_caption,
    format_full_telegram_message,
    send_daily_morning_heartbeat
)


class TestReconPipelineResilience(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.orig_db_file = recon_pipeline.DATABASE_FILE
        recon_pipeline.DATABASE_FILE = os.path.join(self.test_dir, "test_known_docs.json")

    def tearDown(self):
        recon_pipeline.DATABASE_FILE = self.orig_db_file
        if os.path.exists(self.test_dir):
            for f in os.listdir(self.test_dir):
                os.remove(os.path.join(self.test_dir, f))
            os.rmdir(self.test_dir)

    def test_01_safe_html_escaping(self):
        """Kiểm tra khử khuẩn ký tự đặc biệt (&, <, >) tránh lỗi 400 Telegram parse."""
        self.assertEqual(safe_html(None), "")
        self.assertEqual(safe_html("Gói thầu < 15 tỷ & > 5 tỷ"), "Gói thầu &lt; 15 tỷ &amp; &gt; 5 tỷ")
        self.assertEqual(safe_html('Quy chuẩn "PCCC"'), "Quy chuẩn &quot;PCCC&quot;")

    def test_02_load_known_documents_auto_migration(self):
        """Kiểm tra tự động nâng cấp cấu trúc dữ liệu từ List sang Dict chuẩn 100%."""
        # Giả lập file cũ dạng list chứa 3 hash
        legacy_list = ["hash_001", "hash_002", "hash_003"]
        with open(recon_pipeline.DATABASE_FILE, "w", encoding="utf-8") as f:
            json.dump(legacy_list, f)

        # Nạp và kiểm tra tự động chuyển sang Dict
        migrated = load_known_documents()
        self.assertIsInstance(migrated, dict)
        self.assertEqual(len(migrated), 3)
        self.assertIn("hash_001", migrated)
        self.assertEqual(migrated["hash_001"]["id"], "hash_001")

        # Kiểm tra ghi đè và đọc lại vẫn là Dict
        migrated["hash_004"] = {"id": "hash_004", "title": "New Doc"}
        save_known_documents(migrated)

        reloaded = load_known_documents()
        self.assertIsInstance(reloaded, dict)
        self.assertEqual(len(reloaded), 4)

    def test_03_compact_caption_length_and_structure(self):
        """Kiểm tra Caption gửi PDF luôn dưới 850 ký tự và không vỡ thẻ HTML."""
        item = {
            "title": "Nghị định quy định chi tiết thi hành một số điều của Luật Đấu thầu về lựa chọn nhà thầu & thực hiện hợp đồng gói thầu < 50 tỷ đồng trong các dự án đầu tư xây dựng công trình",
            "published": "21/08/2026",
            "source_name": "Cổng TTĐT Chính phủ"
        }
        doc_meta = {
            "loai_van_ban": "Nghị định",
            "ngay_ban_hanh": "21/08/2026"
        }
        ai_data = {
            "so_hieu_clean": "214/2025/NĐ-CP",
            "ngay_hieu_luc": "01/01/2026",
            "van_ban_thay_the": "Nghị định 24/2024/NĐ-CP",
            "chuyen_tiep_ngan": "Hợp đồng đã ký trước 01/01/2026 tiếp tục thực hiện.",
            "goi_thau_tags": ["#Đấu_thầu", "#Hợp_đồng", "#Xây_lắp"],
            "summary_top3": [
                "1. Quy định tỷ lệ tạm ứng tối thiểu 10% và tối đa 50% giá trị hợp đồng.",
                "2. Rút ngắn thời gian thanh toán KBNN xuống 02 ngày làm việc."
            ]
        }

        caption = format_compact_caption(item, doc_meta, ai_data)
        self.assertLessEqual(len(caption), 850, f"Caption quá dài ({len(caption)} ký tự)")
        self.assertIn("<b>Nghị định</b>", caption)
        self.assertIn("<code>214/2025/NĐ-CP</code>", caption)
        self.assertIn("&lt; 50 tỷ", caption)
        self.assertIn("&amp;", caption)
        self.assertIn("<blockquote>", caption)
        self.assertIn("</blockquote>", caption)

    def test_04_full_telegram_message(self):
        """Kiểm tra tin nhắn phân tích đầy đủ."""
        item = {
            "title": "Thông tư số 36/2026/TT-BXD Quản lý chi phí ĐTXD",
            "source_name": "Bộ Xây dựng",
            "published": "21/08/2026"
        }
        doc_meta = {"loai_van_ban": "Thông tư", "ngay_ban_hanh": "21/08/2026"}
        ai_data = {
            "so_hieu_clean": "36/2026/TT-BXD",
            "ngay_hieu_luc": "01/07/2026",
            "van_ban_thay_the": "Thông tư 11/2021/TT-BXD",
            "chuyen_tiep_ngan": "Dự toán đã duyệt trước ngày 01/07/2026 không phải phê duyệt lại.",
            "goi_thau_tags": ["#Dự_toán", "#Định_mức"],
            "summary_top3": ["Cập nhật hệ số nhân công.", "Sửa đổi định mức ca máy."]
        }

        msg, markup = format_full_telegram_message(
            item, doc_meta, ai_data,
            telegraph_url="https://telegra.ph/sample",
            clean_link="https://moc.gov.vn"
        )
        self.assertIn("36/2026/TT-BXD", msg)
        self.assertIn("inline_keyboard", markup)
        self.assertEqual(len(markup["inline_keyboard"]), 2)

    def test_05_heartbeat_zero_docs(self):
        """Kiểm tra tạo thông điệp Heartbeat 07:00 sáng khi không có luật mới."""
        res = send_daily_morning_heartbeat(
            new_matched_count=0,
            sources_scanned=5,
            total_entries=50
        )
        self.assertIsInstance(res, bool)


if __name__ == "__main__":
    unittest.main()
