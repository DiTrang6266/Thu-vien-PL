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
    print("🚀 BẮT ĐẦU CHẠY THỬ NGHIỆM PHÂN TÍCH AI THỰC TẾ...")

    # Dữ liệu đối chiếu thực tế giữa Nghị định 24/2024/NĐ-CP và quy định cũ
    old_text = """
Điều 12. Thời gian chuẩn bị và đánh giá hồ sơ dự thầu trong nước
1. Thời gian chuẩn bị hồ sơ dự thầu đối với gói thầu xây lắp quy mô nhỏ tối thiểu là 10 ngày kể từ ngày đầu tiên phát hành E-HSMT.
2. Thời gian đánh giá hồ sơ dự thầu tối đa là 45 ngày đối với đấu thầu rộng rãi kể từ ngày mở thầu.
3. Hạn mức chỉ định thầu đối với gói thầu xây lắp là không quá 1.000.000.000 đồng (một tỷ đồng) thuộc dự án đầu tư phát triển.
4. Bảo đảm dự thầu được thực hiện bằng thư bảo lãnh của tổ chức tín dụng hoặc đặt cọc bằng séc.
"""

    new_text = """
Điều 12. Thời gian chuẩn bị và đánh giá hồ sơ dự thầu qua mạng
1. Thời gian chuẩn bị E-HSDT đối với gói thầu xây lắp thông thường tối thiểu là 18 ngày, gói thầu quy mô nhỏ tối thiểu là 12 ngày kể từ ngày E-HSMT được phát hành trên Hệ thống mạng đấu thầu quốc gia.
2. Thời gian đánh giá E-HSDT tối đa là 25 ngày đối với đấu thầu rộng rãi (rút ngắn 20 ngày so với trước đây để đẩy nhanh tiến độ giải ngân đầu tư công).
3. Bãi bỏ hạn mức chỉ định thầu cứng 1 tỷ đồng cũ, áp dụng hạn mức và các trường hợp đặc thù theo quy định tại Điều 23 của Luật Đấu thầu 2023.
4. Bắt buộc 100% sử dụng Bảo lãnh dự thầu điện tử (E-Guarantee) được phát hành và xác thực tự động trực tiếp kết nối giữa ngân hàng thương mại và Hệ thống mạng đấu thầu quốc gia.
"""

    item = {
        "id": "live_test_nd24_vs_nd63",
        "title": "Nghị định 24/2024/NĐ-CP (Quy định chi tiết thi hành Luật Đấu thầu về lựa chọn nhà thầu)",
        "link": "https://congbao.chinhphu.vn",
        "summary": f"Văn bản cũ:\n{old_text}\n\nVăn bản mới sửa đổi bổ sung:\n{new_text}",
        "published": "Mới cập nhật",
        "source_name": "Công báo Chính phủ / Bộ Kế hoạch & Đầu tư",
        "categories": ["DAU_THAU", "QUAN_LY_CHI_PHI", "DAU_TU_CONG"]
    }

    ai_analyzer = LegalAIAnalyzer()
    telegraph_pub = TelegraphPublisher()

    print("🧠 Đang chuyển văn bản cho Gemini AI phân tích chuyên sâu...")
    success = process_and_send_alert(item, ai_analyzer, telegraph_pub)

    if success:
        print("✅ THÀNH CÔNG RỰC RỠ! Đã gửi bản tin phân tích chi tiết kèm Instant View vào Telegram của bạn.")
    else:
        print("⚠️ Đã phân tích xong nhưng gặp vấn đề khi gửi Telegram (kiểm tra token/chat_id).")


if __name__ == "__main__":
    run_live_test()
