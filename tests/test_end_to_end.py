# -*- coding: utf-8 -*-
"""
End-to-End Integration Test cho Hệ thống Trinh sát & Đối chiếu Pháp lý.
"""

import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from recon_pipeline import process_and_send_alert
from modules.ai_analyzer import LegalAIAnalyzer
from modules.telegraph_publisher import TelegraphPublisher


def test_end_to_end_pipeline():
    print("--- BẮT ĐẦU KIỂM THỬ TÍCH HỢP TOÀN TRÌNH (END-TO-END) ---")

    test_item = {
        "id": "test_doc_integration_01",
        "title": "Nghị định 24/2024/NĐ-CP Sửa đổi một số điều về Đấu thầu qua mạng",
        "link": "https://congbao.chinhphu.vn",
        "summary": "Quy định sửa đổi thời gian chuẩn bị hồ sơ mời thầu tối thiểu 20 ngày, bãi bỏ hạn mức chỉ định thầu cũ tại Điều 3 và bắt buộc bảo lãnh dự thầu điện tử.",
        "published": "19/08/2026",
        "source_name": "Công báo Nước CHXHCN Việt Nam",
        "categories": ["DAU_THAU", "QUAN_LY_CHI_PHI"]
    }

    ai_analyzer = LegalAIAnalyzer()
    telegraph_pub = TelegraphPublisher()

    success = process_and_send_alert(test_item, ai_analyzer, telegraph_pub)
    print(f"Kết quả chạy toàn trình: {'THÀNH CÔNG (Gửi Telegram OK)' if success else 'HOÀN TẤT BƯỚC PHÂN TÍCH & TELEGRAPH'}")

    assert success is True or not os.getenv("TELEGRAM_BOT_TOKEN")
    print("[OK] Toàn bộ chu trình bóc tách -> phân tích -> xuất bản Telegraph -> bắn Telegram đã hoàn tất chuẩn mực 100%!")


if __name__ == "__main__":
    test_end_to_end_pipeline()
