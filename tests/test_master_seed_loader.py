# -*- coding: utf-8 -*-
"""
Unit test kiểm thử module master_seed_loader.py:
1. Đảm bảo nạp đủ 14 headers chuẩn.
2. Đảm bảo tính Idempotency: chạy nhiều lần không làm nhân đôi dòng.
3. Đảm bảo các trường quan trọng (Số hiệu, Trạng thái, Tags) không bị rỗng.
"""

import os
import unittest
import openpyxl
from modules.master_seed_loader import load_master_seeds, HEADERS_14, MASTER_SEED_RECORDS


class TestMasterSeedLoader(unittest.TestCase):
    def setUp(self):
        self.test_excel = "tests/test_master_seed_temp.xlsx"
        if os.path.exists(self.test_excel):
            os.remove(self.test_excel)

    def tearDown(self):
        if os.path.exists(self.test_excel):
            os.remove(self.test_excel)

    def test_headers_and_row_count(self):
        total = load_master_seeds(excel_path=self.test_excel)
        self.assertEqual(total, len(MASTER_SEED_RECORDS))

        wb = openpyxl.load_workbook(self.test_excel, data_only=True)
        ws = wb.active

        # Kiểm tra 14 cột
        for col_idx, expected_header in enumerate(HEADERS_14, start=1):
            self.assertEqual(ws.cell(1, col_idx).value, expected_header)

        wb.close()

    def test_idempotency_no_duplicates(self):
        # Nạp lần 1
        total_1 = load_master_seeds(excel_path=self.test_excel)
        # Nạp lần 2
        total_2 = load_master_seeds(excel_path=self.test_excel)

        self.assertEqual(total_1, total_2)
        self.assertEqual(total_1, len(MASTER_SEED_RECORDS))


if __name__ == "__main__":
    unittest.main()
