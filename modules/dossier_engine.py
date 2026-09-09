# -*- coding: utf-8 -*-
"""
Module: dossier_engine.py
Mục đích: Động cơ Đúc Hồ sơ Dự án Xây dựng (Word Template Engine).
Nguyên tắc: Đứng trên vai người khổng lồ, Code ít nhất - Hiệu quả cao nhất, Chuẩn thể thức NĐ 30.
"""

import os
import sys
from typing import Dict, Any, Optional, List
from docxtpl import DocxTemplate

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from modules.word_grounding_engine import get_active_legal_bases


DEFAULT_LEGAL_BASES_PREPARATION = [
    "Căn cứ Luật Xây dựng số 135/2025/QH15 ngày 10/12/2025;",
    "Căn cứ Luật Ngân sách nhà nước số 89/2025/QH15 ngày 25/6/2025;",
    "Căn cứ Nghị định số 217/2026/NĐ-CP ngày 17/6/2026 của Chính phủ quy định chi tiết một số điều của Luật Xây dựng về quản lý hoạt động xây dựng;",
    "Căn cứ Thông tư số 101/2026/TT-BQP ngày 09/7/2026 của Bộ Quốc phòng quy định chi tiết và biện pháp thực hiện một số nội dung Luật Xây dựng thuộc phạm vi quản lý của Bộ Quốc phòng;",
    "Căn cứ Thông tư số 38/2026/TT-BXD ngày 26/6/2026 của Bộ Xây dựng ban hành hệ thống định mức dự toán xây dựng công trình và định mức chi phí tư vấn đầu tư xây dựng;",
    "Căn cứ Quy định số 3000/QyĐ-PKKQ ngày 08/6/2026 của Quân chủng PK-KQ về đầu tư, mua sắm, sản xuất quốc phòng trong Quân chủng Phòng không - Không quân;"
]


def render_qd_du_toan_chuan_bi(
    data: Dict[str, Any],
    template_path: Optional[str] = None,
    output_path: Optional[str] = None
) -> str:
    """
    Đúc Quyết định phê duyệt nhiệm vụ và dự toán chi phí chuẩn bị dự án / lập Báo cáo KT-KT.
    """
    resolved_tpl_path = template_path or os.path.join(
        BASE_DIR, "templates", "phoi_QD_du_toan_chuan_bi.docx"
    )

    if not os.path.exists(resolved_tpl_path):
        raise FileNotFoundError(f"Không tìm thấy phôi mẫu: {resolved_tpl_path}")

    # Chuẩn bị context với các giá trị mặc định chuẩn thể thức
    context = {
        "co_quan_chu_quan": data.get("co_quan_chu_quan", "QC PHÒNG KHÔNG - KHÔNG QUÂN"),
        "don_vi_ban_hanh_dong1": data.get("don_vi_ban_hanh_dong1", "TRƯỜNG CAO ĐẲNG KỸ THUẬT"),
        "don_vi_ban_hanh_dong2": data.get("don_vi_ban_hanh_dong2", "PHÒNG KHÔNG - KHÔNG QUÂN"),
        "so_quyet_dinh": data.get("so_quyet_dinh", "       /QĐ-TCĐ"),
        "dia_danh_ngay_thang": data.get("dia_danh_ngay_thang", "Hà Nội, ngày      tháng 8 năm 2026"),
        "ten_cong_trinh": data.get("ten_cong_trinh", "Bảo trì, sửa chữa công trình phổ thông từ nguồn kinh phí thường xuyên năm 2026"),
        "nguon_von": data.get("nguon_von", "nguồn kinh phí thường xuyên năm 2026"),
        "ten_don_vi": data.get("ten_don_vi", "Trường Cao đẳng Kỹ thuật PK-KQ"),
        "chuc_danh_nguoi_ky_quyet_dinh": data.get("chuc_danh_nguoi_ky_quyet_dinh", "HIỆU TRƯỞNG TRƯỜNG CAO ĐẲNG KỸ THUẬT PK-KQ"),
        "danh_sach_can_cu": data.get("danh_sach_can_cu") or DEFAULT_LEGAL_BASES_PREPARATION,
        "so_qd_ke_hoach": data.get("so_qd_ke_hoach", "          /QĐ-TCĐ ngày      /8/2026"),
        "don_vi_de_nghi": data.get("don_vi_de_nghi", "Trưởng ban Quản lý công trình"),
        "chi_phi_lap_bcktkt_so": data.get("chi_phi_lap_bcktkt_so", "71.200.175"),
        "chi_phi_lap_bcktkt_chu": data.get("chi_phi_lap_bcktkt_chu", "Bảy mươi mốt triệu, hai trăm nghìn, một trăm bảy mươi lăm đồng"),
        "ban_quan_ly": data.get("ban_quan_ly", "Ban Quản lý công trình"),
        "chuc_vu_nguoi_ky": data.get("chuc_vu_nguoi_ky", "HIỆU TRƯỞNG"),
        "ho_ten_nguoi_ky": data.get("ho_ten_nguoi_ky", "Đại tá Nguyễn Hữu Cương")
    }

    # Đường dẫn file xuất ra
    if not output_path:
        out_dir = os.path.join(BASE_DIR, "data", "output_ho_so")
        os.makedirs(out_dir, exist_ok=True)
        filename = f"QD_Phe_duyet_Du_toan_{context['so_quyet_dinh'].replace('/', '_').replace(' ', '')}.docx"
        output_path = os.path.join(out_dir, filename)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Đúc văn bản bằng docxtpl
    tpl = DocxTemplate(resolved_tpl_path)
    tpl.render(context)
    tpl.save(output_path)

    return output_path
