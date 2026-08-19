# -*- coding: utf-8 -*-
"""
Unit test kiểm thử module legal_parser và legal_diff.
"""

import os
import sys

# Đảm bảo in tiếng Việt mượt mà trên console Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Thêm thư mục gốc vào path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.legal_parser import LegalDocumentParser
from modules.legal_diff import LegalDocumentDiffer


def test_parsing_and_diff():
    old_law_text = """
CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
Độc lập - Tự do - Hạnh phúc

NGHỊ ĐỊNH
Quy định chi tiết thi hành Luật Đấu thầu

CHƯƠNG I
QUY ĐỊNH CHUNG

Điều 1. Phạm vi điều chỉnh
1. Nghị định này quy định chi tiết một số điều của Luật Đấu thầu về lựa chọn nhà thầu.
2. Việc lựa chọn nhà đầu tư thực hiện theo nghị định riêng.

Điều 2. Thời gian tổ chức lựa chọn nhà thầu
1. Thời gian chuẩn bị hồ sơ dự thầu tối thiểu là 15 ngày đối với đấu thầu trong nước.
2. Thời gian đánh giá hồ sơ dự thầu tối đa là 30 ngày kể từ ngày mở thầu.

Điều 3. Hạn mức chỉ định thầu
1. Gói thầu xây lắp không quá 1.000.000.000 đồng (một tỷ đồng).
2. Gói thầu tư vấn không quá 500.000.000 đồng.
"""

    new_law_text = """
CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
Độc lập - Tự do - Hạnh phúc

NGHỊ ĐỊNH
Sửa đổi, bổ sung một số điều của Nghị định quy định chi tiết Luật Đấu thầu

CHƯƠNG I
QUY ĐỊNH CHUNG

Điều 1. Phạm vi điều chỉnh
1. Nghị định này quy định chi tiết một số điều của Luật Đấu thầu về lựa chọn nhà thầu và nhà đầu tư.

Điều 2. Thời gian tổ chức lựa chọn nhà thầu
1. Thời gian chuẩn bị hồ sơ dự thầu tối thiểu là 20 ngày đối với đấu thầu trong nước.
2. Thời gian đánh giá hồ sơ dự thầu tối đa là 45 ngày kể từ ngày mở thầu.

Điều 4. Quy định về hồ sơ điện tử
1. Toàn bộ quy trình đấu thầu phải thực hiện qua Hệ thống mạng đấu thầu quốc gia.
"""

    parser = LegalDocumentParser()
    differ = LegalDocumentDiffer()

    old_parsed = parser.parse_text(old_law_text, doc_name="Nghị định cũ")
    new_parsed = parser.parse_text(new_law_text, doc_name="Nghị định mới")

    print(f"Old Doc Articles: {list(old_parsed['articles'].keys())}")
    print(f"New Doc Articles: {list(new_parsed['articles'].keys())}")

    assert "Điều 1" in old_parsed["articles"]
    assert "Điều 2" in old_parsed["articles"]
    assert "Điều 3" in old_parsed["articles"]
    assert "Điều 4" in new_parsed["articles"]

    diff_results = differ.compare_articles(old_parsed["articles"], new_parsed["articles"])

    print("\n--- KẾT QUẢ ĐỐI CHIẾU SO SÁNH ---")
    for item in diff_results:
        print(f"[{item['status']}] {item['article_id']}: {item['title']}")
        if item["status"] == "SỬA ĐỔI / THAY THẾ":
            print(f"   Markdown Redline: {item['redline_md']}")

    # Kiểm tra tính năng verify exact quote
    quote_valid = "Thời gian chuẩn bị hồ sơ dự thầu tối thiểu là 20 ngày"
    quote_invalid = "Thời gian chuẩn bị hồ sơ dự thầu tối thiểu là 99 ngày"

    assert differ.verify_exact_quote(quote_valid, new_law_text) is True
    assert differ.verify_exact_quote(quote_invalid, new_law_text) is False

    print("\n[OK] TẤT CẢ CÁC BƯỚC KIỂM THỬ ĐÃ THÀNH CÔNG 100%!")


if __name__ == "__main__":
    test_parsing_and_diff()
