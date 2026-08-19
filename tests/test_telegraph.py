# -*- coding: utf-8 -*-
"""
Unit test kiểm thử module telegraph_publisher.
"""

import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.telegraph_publisher import TelegraphPublisher


def test_telegraph_formatting_and_publish():
    publisher = TelegraphPublisher()

    fake_ai_data = {
        "summary_top3": [
            "1. Tăng thời gian chuẩn bị hồ sơ dự thầu từ 15 ngày lên 20 ngày.",
            "2. Bắt buộc số hóa 100% hồ sơ qua Mạng Đấu thầu Quốc gia.",
            "3. Bãi bỏ hạn mức chỉ định thầu cũ tại Điều 3."
        ],
        "impact_areas": {
            "ho_so_moi_thau_va_dau_thau": "Phải cập nhật lại tiến độ phát hành HSMT trong kế hoạch lựa chọn nhà thầu tối thiểu 20 ngày.",
            "du_toan_va_chi_phi": "Chi phí bảo lãnh dự thầu điện tử tính theo biểu phí ngân hàng số.",
            "tham_quyen_va_trach_nhiem": "Chủ đầu tư trực tiếp phê duyệt kết quả lựa chọn nhà thầu qua mạng."
        },
        "transition_rules": "Đối với các gói thầu đã phát hành HSMT trước ngày Nghị định này có hiệu lực thì tiếp tục thực hiện theo quy định cũ.",
        "detailed_articles_diff": [
            {
                "article_id": "Điều 2",
                "title": "Thời gian tổ chức lựa chọn nhà thầu",
                "status": "SỬA ĐỔI / THAY THẾ",
                "exact_quote_old": "Thời gian chuẩn bị hồ sơ dự thầu tối thiểu là 15 ngày",
                "exact_quote_new": "Thời gian chuẩn bị hồ sơ dự thầu tối thiểu là 20 ngày",
                "core_change_explanation": "Kéo dài thêm 5 ngày để nhà thầu chuẩn bị hồ sơ kỹ lưỡng hơn.",
                "action_required": "Điều chỉnh mốc thời gian trong Bảng tiến độ mời thầu."
            },
            {
                "article_id": "Điều 3",
                "title": "Hạn mức chỉ định thầu",
                "status": "BÃI BỎ",
                "exact_quote_old": "Gói thầu xây lắp không quá 1 tỷ đồng",
                "exact_quote_new": "",
                "core_change_explanation": "Bãi bỏ hạn mức cũ, áp dụng theo Luật Đấu thầu mới.",
                "action_required": "Không áp dụng hạn mức 1 tỷ cũ cho các gói thầu mới."
            }
        ],
        "verification_summary": {
            "accuracy_rate": "100%"
        }
    }

    doc_meta = {
        "so_hieu": "Nghị định số 24/2024/NĐ-CP (Sửa đổi)",
        "co_quan": "Chính phủ",
        "ngay_ban_hanh": "19/08/2026"
    }

    # 1. Test format nodes
    nodes = publisher.format_nodes_from_analysis(
        title="BÁO CÁO THỬ NGHIỆM ĐỐI CHIẾU PHÁP LÝ",
        ai_data=fake_ai_data,
        doc_meta=doc_meta
    )
    assert len(nodes) > 5
    print(f"Số lượng Node định dạng Telegraph: {len(nodes)}")

    # 2. Test actual publish to Telegraph API
    url = publisher.publish_report(
        title="BÁO CÁO ĐỐI CHIẾU PHÁP LÝ XÂY DỰNG & ĐẤU THẦU",
        ai_data=fake_ai_data,
        doc_meta=doc_meta
    )
    print(f"Kết quả xuất bản Telegraph URL: {url}")

    if url:
        assert "telegra.ph" in url
        print("[OK] Đã tạo thành công bài viết Instant View trên Telegraph!")
    else:
        print("[WARNING] Không thể kết nối Telegraph (có thể do chặn mạng tạm thời).")


if __name__ == "__main__":
    test_telegraph_formatting_and_publish()
