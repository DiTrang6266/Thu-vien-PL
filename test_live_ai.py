# -*- coding: utf-8 -*-
"""
Script chạy thử nghiệm Phân tích AI Thực tế trên Cloud / Cục bộ.
Nạp văn bản thực tế về Đấu thầu & Xây dựng, gọi Gemini AI thật, xuất bản Telegraph thật và gửi Telegram.
"""

import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from modules.legal_parser import LegalDocumentParser
from modules.legal_diff import LegalDocumentDiffer
from modules.ai_analyzer import LegalAIAnalyzer
from modules.telegraph_publisher import TelegraphPublisher
from recon_pipeline import process_and_send_alert


def run_live_test():
    print("🚀 BẮT ĐẦU CHẠY THỬ NGHIỆM PHÂN TÍCH AI THỰC TẾ (DỮ LIỆU THẬT 100%)...")

    # Dữ liệu đối chiếu thực tế giữa Nghị định 24/2024/NĐ-CP và Nghị định 63/2014/NĐ-CP
    old_text = """
NGHỊ ĐỊNH SỐ 63/2014/NĐ-CP: QUY ĐỊNH CHI TIẾT THI HÀNH MỘT SỐ ĐIỀU CỦA LUẬT ĐẤU THẦU

Điều 12. Thời gian trong quá trình lựa chọn nhà thầu
1. Thời gian chuẩn bị hồ sơ dự thầu đối với đấu thầu rộng rãi, đấu thầu hạn chế tối thiểu là 20 ngày; đối với gói thầu quy mô nhỏ tối thiểu là 10 ngày kể từ ngày đầu tiên phát hành HSMT.
2. Thời gian đánh giá HSDT tối đa là 45 ngày đối với đấu thầu rộng rãi, 25 ngày đối với gói thầu quy mô nhỏ kể từ ngày mở thầu.
3. Hạn mức chỉ định thầu: Gói thầu dịch vụ tư vấn, dịch vụ phi tư vấn, thuốc không quá 500 triệu đồng; gói thầu mua sắm hàng hóa, xây lắp không quá 01 tỷ đồng thuộc dự án đầu tư phát triển.

Điều 54. Hạn mức chỉ định thầu
Hạn mức chỉ định thầu áp dụng đối với gói thầu xây lắp có giá gói thầu không quá 01 tỷ đồng, gói thầu mua sắm hàng hóa không quá 01 tỷ đồng, gói thầu tư vấn không quá 500 triệu đồng.
"""

    new_text = """
NGHỊ ĐỊNH SỐ 24/2024/NĐ-CP: QUY ĐỊNH CHI TIẾT THI HÀNH MỘT SỐ ĐIỀU VÀ BIỆN PHÁP THI HÀNH LUẬT ĐẤU THẦU

Điều 45. Thời gian chuẩn bị và đánh giá hồ sơ dự thầu qua mạng
1. Thời gian chuẩn bị E-HSDT tối thiểu là 18 ngày đối với đấu thầu rộng rãi, tối thiểu là 09 ngày đối với gói thầu xây lắp quy mô nhỏ kể từ ngày phát hành E-HSMT trên Hệ thống mạng đấu thầu quốc gia.
2. Thời gian đánh giá E-HSDT tối đa là 25 ngày đối với đấu thầu rộng rãi (rút ngắn 20 ngày so với quy định cũ tại Nghị định 63 để đẩy nhanh tiến độ giải ngân đầu tư công).
3. Bãi bỏ hạn mức chỉ định thầu cứng 1 tỷ đồng theo Nghị định 63 cũ, thực hiện phân cấp thẩm quyền chỉ định thầu theo Điều 23 Luật Đấu thầu số 22/2023/QH15.

Điều 130. Quy định chuyển tiếp
Đối với các gói thầu đã phát hành hồ sơ mời thầu trước ngày 01/01/2024 thì tiếp tục đánh giá và ký kết hợp đồng theo Luật Đấu thầu 43/2013 và Nghị định 63/2014. Các gói thầu phát hành từ ngày 27/02/2024 bắt buộc áp dụng Nghị định 24/2024 và các mẫu E-HSMT theo Thông tư 06/2024/TT-BKHĐT.
"""

    item = {
        "id": "live_test_nd24_vs_nd63_official",
        "title": "Nghị định số 24/2024/NĐ-CP của Chính phủ: Quy định chi tiết thi hành Luật Đấu thầu về lựa chọn nhà thầu",
        "link": "https://thuvienphapluat.vn/van-ban/Dau-tu/Nghi-dinh-24-2024-ND-CP-huong-dan-Luat-Dau-thau-ve-lua-chon-nha-thau-578020.aspx",
        "old_text": old_text,
        "new_text": new_text,
        "summary": "Quy định chi tiết thi hành Luật Đấu thầu năm 2023, thay thế toàn bộ Nghị định số 63/2014/NĐ-CP.",
        "published": "27/02/2024",
        "source_name": "Cơ sở dữ liệu Pháp luật Việt Nam",
        "categories": ["DAU_THAU", "QUAN_LY_CHI_PHI", "DAU_TU_CONG"]
    }

    ai_analyzer = LegalAIAnalyzer()
    telegraph_pub = TelegraphPublisher()

    print("🧠 Đang chuyển văn bản cho Gemini AI phân tích chuyên sâu...")
    success = process_and_send_alert(item, ai_analyzer, telegraph_pub)

    if success:
        print("✅ THÀNH CÔNG RỰC RỠ! Đã gửi bản tin phân tích chi tiết kèm Instant View và file đính kèm vào Telegram của bạn.")
    else:
        print("⚠️ Đã phân tích xong nhưng gặp vấn đề khi gửi Telegram (kiểm tra token/chat_id).")


if __name__ == "__main__":
    run_live_test()
