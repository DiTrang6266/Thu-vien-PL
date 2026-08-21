# -*- coding: utf-8 -*-
"""
Module: master_seed_loader.py
Mục đích: Nạp hạt giống toàn bộ 86 văn bản pháp luật nền tảng cốt lõi vào Sổ cái Kho_Can_Cu_Phap_Ly.xlsx.
"""

import os
import sys
import openpyxl
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from modules.legal_db_sync import HEADERS_14, apply_table_formatting

EXCEL_PATH = os.path.join(BASE_DIR, "Kho_Can_Cu_Phap_Ly.xlsx")

MASTER_SEED_RECORDS = [
    {
        "linh_vuc": "Quy hoạch Xây dựng", "loai_vb": "Luật", "so_hieu": "30/2009/QH12",
        "trich_yeu": "Luật Quy hoạch đô thị năm 2009", "co_quan": "Quốc hội",
        "ngay_bh": "17/06/2009", "ngay_hl": "01/01/2010", "trang_thai": "Hết hiệu lực",
        "thay_the": "Bị thay thế bởi Luật Quy hoạch đô thị và nông thôn số 47/2024/QH15", "chuyen_tiep": "Căn cứ pháp lý nền tảng cho việc lập, thẩm định và phê duyệt điều chỉnh Quy hoạch Tổng mặt bằng 1/500 doanh trại và khu chức năng",
        "tags": "ALL, QUY_HOACH, TV-01, TV-02, BQP", "link_iv": ""
    },
    {
        "linh_vuc": "Quy hoạch Xây dựng", "loai_vb": "Nghị định", "so_hieu": "44/2015/NĐ-CP",
        "trich_yeu": "Quy định chi tiết một số nội dung về quy hoạch xây dựng", "co_quan": "Chính phủ",
        "ngay_bh": "06/05/2015", "ngay_hl": "30/06/2015", "trang_thai": "Đang có hiệu lực",
        "thay_the": "Được sửa đổi, bổ sung bởi Nghị định số 35/2023/NĐ-CP và Nghị định số 72/2019/NĐ-CP", "chuyen_tiep": "Quy định trình tự, thủ tục lập và phê duyệt Quy hoạch chi tiết và Quy hoạch Tổng mặt bằng công trình",
        "tags": "ALL, QUY_HOACH, TV-01, TV-02, QLDA", "link_iv": ""
    },
    {
        "linh_vuc": "Quy hoạch Xây dựng", "loai_vb": "Thông tư", "so_hieu": "04/2022/TT-BXD",
        "trich_yeu": "Quy định về hồ sơ nhiệm vụ và hồ sơ đồ án quy hoạch xây dựng vùng liên huyện, quy hoạch xây dựng vùng huyện, quy hoạch đô thị, quy hoạch xây dựng khu chức năng và quy hoạch nông thôn", "co_quan": "Bộ Xây dựng",
        "ngay_bh": "24/10/2022", "ngay_hl": "01/01/2023", "trang_thai": "Đang có hiệu lực",
        "thay_the": "Thay thế Thông tư 12/2016/TT-BXD và Thông tư 02/2017/TT-BXD", "chuyen_tiep": "Quy định thành phần hồ sơ bản vẽ, thuyết minh và quy cách đồ án quy hoạch Tổng mặt bằng tỷ lệ 1/500 gói TV-01",
        "tags": "QUY_HOACH, TV-01, HO_SO_QUY_HOACH", "link_iv": ""
    },
    {
        "linh_vuc": "Quy hoạch Xây dựng", "loai_vb": "Thông tư", "so_hieu": "20/2019/TT-BXD",
        "trich_yeu": "Hướng dẫn xác định, quản lý chi phí quy hoạch xây dựng và quy hoạch đô thị", "co_quan": "Bộ Xây dựng",
        "ngay_bh": "31/12/2019", "ngay_hl": "15/02/2020", "trang_thai": "Đang có hiệu lực",
        "thay_the": "Thay thế Thông tư 01/2013/TT-BXD", "chuyen_tiep": "Căn cứ lập dự toán chi phí gói thầu TV-01 Tư vấn lập quy hoạch Tổng mặt bằng tỷ lệ 1/500",
        "tags": "QUY_HOACH, CHI_PHI_QUY_HOACH, DU_TOAN, TV-01", "link_iv": ""
    },
    {
        "linh_vuc": "Quy chuẩn Xây dựng", "loai_vb": "Thông tư", "so_hieu": "01/2021/TT-BXD",
        "trich_yeu": "Ban hành Quy chuẩn kỹ thuật quốc gia về Quy hoạch xây dựng (Mã số: QCVN 01:2021/BXD)", "co_quan": "Bộ Xây dựng",
        "ngay_bh": "19/05/2021", "ngay_hl": "05/07/2021", "trang_thai": "Đang có hiệu lực",
        "thay_the": "Thay thế QCVN 01:2019/BXD ban hành kèm Thông tư 22/2019/TT-BXD", "chuyen_tiep": "Quy chuẩn bắt buộc áp dụng cho gói TV-01 về mật độ xây dựng, khoảng lùi công trình, khoảng cách an toàn PCCC, chỉ giới đường đỏ",
        "tags": "QCVN, QUY_HOACH, TV-01, TV-02, TV-04, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Khảo sát & Đo đạc", "loai_vb": "Luật", "so_hieu": "27/2018/QH14",
        "trich_yeu": "Luật Đo đạc và bản đồ năm 2018", "co_quan": "Quốc hội",
        "ngay_bh": "14/06/2018", "ngay_hl": "01/01/2019", "trang_thai": "Đang có hiệu lực",
        "thay_the": "None", "chuyen_tiep": "Căn cứ pháp lý cho công tác đo đạc khảo sát địa hình, trắc địa công trình phục vụ lập quy hoạch TV-01 và khảo sát TV-02",
        "tags": "KHAO_SAT, DO_DAC, TV-01, TV-02, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Khảo sát & Đo đạc", "loai_vb": "Nghị định", "so_hieu": "27/2019/NĐ-CP",
        "trich_yeu": "Quy định chi tiết một số điều của Luật Đo đạc và bản đồ", "co_quan": "Chính phủ",
        "ngay_bh": "13/03/2019", "ngay_hl": "01/05/2019", "trang_thai": "Đang có hiệu lực",
        "thay_the": "Được sửa đổi, bổ sung bởi Nghị định 136/2021/NĐ-CP", "chuyen_tiep": "Quy định quy chuẩn đo đạc bản đồ địa hình tỷ lệ 1/500 phục vụ lập quy hoạch TMB và thiết kế xây dựng",
        "tags": "KHAO_SAT, DO_DAC, TV-01, TV-02, XD-01", "link_iv": ""
    }
,
    {
        "linh_vuc": "Xây dựng & Quản lý dự án", "loai_vb": "Luật", "so_hieu": "50/2014/QH13",
        "trich_yeu": "Luật Xây dựng năm 2014", "co_quan": "Quốc hội",
        "ngay_bh": "18/06/2014", "ngay_hl": "01/01/2015", "trang_thai": "Hết hiệu lực",
        "thay_the": "Bị thay thế bởi Luật Xây dựng số 135/2025/QH15", "chuyen_tiep": "Dự án đã phê duyệt trước thời điểm luật mới thực hiện theo quy định chuyển tiếp",
        "tags": "ALL, TV-01, TV-02, TV-03, TV-04, TV-05, TV-08, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Xây dựng & Quản lý dự án", "loai_vb": "Luật", "so_hieu": "135/2025/QH15",
        "trich_yeu": "Luật Xây dựng năm 2025", "co_quan": "Quốc hội",
        "ngay_bh": "28/11/2025", "ngay_hl": "01/07/2026", "trang_thai": "Đang có hiệu lực",
        "thay_the": "Thay thế Luật Xây dựng 50/2014/QH13 và Luật sửa đổi 62/2020/QH14", "chuyen_tiep": "Áp dụng toàn diện cho các dự án đầu tư xây dựng mới",
        "tags": "ALL, TV-01, TV-02, TV-03, TV-04, TV-05, TV-08, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Xây dựng & Quản lý dự án", "loai_vb": "Luật", "so_hieu": "62/2020/QH14",
        "trich_yeu": "Luật sửa đổi, bổ sung một số điều của Luật Xây dựng", "co_quan": "Quốc hội",
        "ngay_bh": "17/06/2020", "ngay_hl": "01/01/2021", "trang_thai": "Hết hiệu lực",
        "thay_the": "Bị thay thế bởi Luật Xây dựng số 135/2025/QH15", "chuyen_tiep": "Quy định chuyển tiếp thẩm định thiết kế, cấp phép",
        "tags": "ALL, TV-01, TV-02, TV-03, TV-04, TV-05, TV-08, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Xây dựng & Quản lý dự án", "loai_vb": "Nghị định", "so_hieu": "15/2021/NĐ-CP",
        "trich_yeu": "Quy định chi tiết một số nội dung về quản lý dự án đầu tư xây dựng", "co_quan": "Chính phủ",
        "ngay_bh": "03/03/2021", "ngay_hl": "03/03/2021", "trang_thai": "Hết hiệu lực",
        "thay_the": "Bị thay thế bởi Nghị định 175/2024/NĐ-CP và Nghị định 217/2026/NĐ-CP", "chuyen_tiep": "Áp dụng cho các dự án đã trình thẩm định giai đoạn 2021-2024",
        "tags": "ALL, QLDA, TV-01, TV-02, TV-03, TV-04, TV-05, TV-08, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Xây dựng & Quản lý dự án", "loai_vb": "Nghị định", "so_hieu": "175/2024/NĐ-CP",
        "trich_yeu": "Quy định chi tiết một số điều và biện pháp thi hành Luật Xây dựng về quản lý hoạt động xây dựng", "co_quan": "Chính phủ",
        "ngay_bh": "30/12/2024", "ngay_hl": "15/02/2025", "trang_thai": "Hết hiệu lực",
        "thay_the": "Bị thay thế bởi Nghị định 217/2026/NĐ-CP", "chuyen_tiep": "Áp dụng giai đoạn chuyển tiếp 2025",
        "tags": "ALL, QLDA, TV-01, TV-02, TV-03, TV-04, TV-05, TV-08, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Xây dựng & Quản lý dự án", "loai_vb": "Nghị định", "so_hieu": "217/2026/NĐ-CP",
        "trich_yeu": "Quy định chi tiết một số điều của Luật Xây dựng về quản lý hoạt động xây dựng", "co_quan": "Chính phủ",
        "ngay_bh": "10/06/2026", "ngay_hl": "01/07/2026", "trang_thai": "Đang có hiệu lực",
        "thay_the": "Thay thế Nghị định 15/2021/NĐ-CP và Nghị định 175/2024/NĐ-CP", "chuyen_tiep": "Căn cứ pháp lý then chốt về quản lý dự án đầu tư xây dựng hiện hành",
        "tags": "ALL, QLDA, TV-01, TV-02, TV-03, TV-04, TV-05, TV-08, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Xây dựng & Quản lý dự án", "loai_vb": "Nghị định", "so_hieu": "35/2023/NĐ-CP",
        "trich_yeu": "Sửa đổi, bổ sung một số điều của các Nghị định thuộc lĩnh vực quản lý nhà nước của Bộ Xây dựng", "co_quan": "Chính phủ",
        "ngay_bh": "20/06/2023", "ngay_hl": "20/06/2023", "trang_thai": "Đang có hiệu lực",
        "thay_the": "None", "chuyen_tiep": "Phân cấp thẩm quyền thẩm định Báo cáo KT-KT và thiết kế dự toán",
        "tags": "ALL, QLDA, TV-01, TV-02, TV-03, TV-04, TV-05, TV-08, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Xây dựng & Quản lý dự án", "loai_vb": "Nghị quyết", "so_hieu": "66.19/2026/NQ-CP",
        "trich_yeu": "Về cắt giảm, phân quyền, đơn giản hóa thủ tục hành chính và cắt giảm, đơn giản hóa điều kiện kinh doanh thuộc phạm vi quản lý của Bộ Nông nghiệp và Môi trường", "co_quan": "Chính phủ",
        "ngay_bh": "18/05/2026", "ngay_hl": "28/02/2027", "trang_thai": "Đang có hiệu lực",
        "thay_the": "None", "chuyen_tiep": "Cắt giảm, phân quyền thủ tục môi trường và thủ tục hành chính",
        "tags": "MOI_TRUONG, TV-01, TV-02, TV-03, TV-04, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Đấu thầu qua mạng", "loai_vb": "Luật", "so_hieu": "22/2023/QH15",
        "trich_yeu": "Luật Đấu thầu năm 2023", "co_quan": "Quốc hội",
        "ngay_bh": "23/06/2023", "ngay_hl": "01/01/2024", "trang_thai": "Đang có hiệu lực",
        "thay_the": "Luật Đấu thầu 43/2013/QH13", "chuyen_tiep": "Gói thầu phát hành HSMT từ 01/01/2024 áp dụng Luật 22",
        "tags": "ALL, DAU_THAU, TV-01, TV-02, TV-03, TV-04, TV-05, TV-06, TV-07, TV-08, TV-09, PTV-01, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Đấu thầu qua mạng", "loai_vb": "Luật", "so_hieu": "57/2024/QH15",
        "trich_yeu": "Luật sửa đổi, bổ sung một số điều của Luật Quy hoạch, Luật Đầu tư, Luật Đầu tư theo phương thức đối tác công tư và Luật Đấu thầu", "co_quan": "Quốc hội",
        "ngay_bh": "29/11/2024", "ngay_hl": "15/01/2025", "trang_thai": "Đang có hiệu lực",
        "thay_the": "None", "chuyen_tiep": "Nâng hạn mức chỉ định thầu và đơn giản hóa thủ tục đầu tư",
        "tags": "ALL, DAU_THAU, TV-01, TV-02, TV-03, TV-04, TV-05, TV-06, TV-07, TV-08, TV-09, PTV-01, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Đấu thầu qua mạng", "loai_vb": "Luật", "so_hieu": "90/2025/QH15",
        "trich_yeu": "Luật sửa đổi bổ sung Luật Đấu thầu", "co_quan": "Quốc hội",
        "ngay_bh": "25/06/2025", "ngay_hl": "01/08/2025", "trang_thai": "Hết hiệu lực",
        "thay_the": "Sửa đổi, bổ sung một số điều của Luật Đấu thầu số 22/2023/QH15", "chuyen_tiep": "Sửa đổi bổ sung cơ chế đấu thầu thuốc, vật tư và mua sắm công",
        "tags": "ALL, DAU_THAU, KHLCNT", "link_iv": ""
    },
    {
        "linh_vuc": "Đấu thầu qua mạng", "loai_vb": "Luật", "so_hieu": "43/2013/QH13",
        "trich_yeu": "Luật Đấu thầu năm 2013", "co_quan": "Quốc hội",
        "ngay_bh": "26/11/2013", "ngay_hl": "01/07/2014", "trang_thai": "Hết hiệu lực",
        "thay_the": "Bị thay thế bởi Luật Đấu thầu 22/2023/QH15", "chuyen_tiep": "Áp dụng cho các gói thầu mở trước 2024",
        "tags": "DAU_THAU, LICHSU", "link_iv": ""
    },
    {
        "linh_vuc": "Đấu thầu qua mạng", "loai_vb": "Nghị định", "so_hieu": "24/2024/NĐ-CP",
        "trich_yeu": "Quy định chi tiết một số điều và biện pháp thi hành Luật Đấu thầu về lựa chọn nhà thầu", "co_quan": "Chính phủ",
        "ngay_bh": "27/02/2024", "ngay_hl": "27/02/2024", "trang_thai": "Hết hiệu lực",
        "thay_the": "Bị thay thế bởi Nghị định 214/2025/NĐ-CP", "chuyen_tiep": "Áp dụng cho các gói thầu phát hành E-HSMT giai đoạn 2024-2025",
        "tags": "ALL, DAU_THAU, TV-01, TV-02, TV-03, TV-04, TV-05, TV-06, TV-07, TV-08, TV-09, PTV-01, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Đấu thầu qua mạng", "loai_vb": "Nghị định", "so_hieu": "214/2025/NĐ-CP",
        "trich_yeu": "Quy định chi tiết một số điều và biện pháp thi hành Luật Đấu thầu về lựa chọn nhà thầu", "co_quan": "Chính phủ",
        "ngay_bh": "15/12/2025", "ngay_hl": "01/01/2026", "trang_thai": "Đang có hiệu lực",
        "thay_the": "Thay thế Nghị định 24/2024/NĐ-CP", "chuyen_tiep": "Quy định toàn diện về lựa chọn nhà thầu qua mạng trên Hệ thống e-GP mới",
        "tags": "ALL, DAU_THAU, TV-01, TV-02, TV-03, TV-04, TV-05, TV-06, TV-07, TV-08, TV-09, PTV-01, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Đấu thầu qua mạng", "loai_vb": "Nghị định", "so_hieu": "63/2014/NĐ-CP",
        "trich_yeu": "Quy định chi tiết thi hành một số điều của Luật Đấu thầu về lựa chọn nhà thầu", "co_quan": "Chính phủ",
        "ngay_bh": "26/06/2014", "ngay_hl": "15/08/2014", "trang_thai": "Hết hiệu lực",
        "thay_the": "Bị thay thế bởi Nghị định 24/2024/NĐ-CP", "chuyen_tiep": "Áp dụng cho gói thầu mở trước 27/02/2024",
        "tags": "DAU_THAU, LICHSU", "link_iv": ""
    },
    {
        "linh_vuc": "Đấu thầu qua mạng", "loai_vb": "Thông tư", "so_hieu": "06/2024/TT-BKHĐT",
        "trich_yeu": "Hướng dẫn việc cung cấp, đăng tải thông tin về lựa chọn nhà thầu và mẫu hồ sơ đấu thầu trên Hệ thống mạng đấu thầu quốc gia", "co_quan": "Bộ Kế hoạch và Đầu tư",
        "ngay_bh": "26/04/2024", "ngay_hl": "26/04/2024", "trang_thai": "Hết hiệu lực",
        "thay_the": "Bị thay thế bởi Thông tư 22/2024/TT-BKHĐT và Thông tư 79/2025/TT-BTC", "chuyen_tiep": "Mẫu E-HSMT giai đoạn đầu 2024",
        "tags": "ALL, DAU_THAU, E_HSMT, TV-01, TV-02, TV-03, TV-04, TV-05, TV-06, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Đấu thầu qua mạng", "loai_vb": "Thông tư", "so_hieu": "22/2024/TT-BKHĐT",
        "trich_yeu": "Hướng dẫn việc cung cấp, đăng tải thông tin về lựa chọn nhà thầu và mẫu hồ sơ đấu thầu trên Hệ thống mạng đấu thầu quốc gia", "co_quan": "Bộ Kế hoạch và Đầu tư",
        "ngay_bh": "15/11/2024", "ngay_hl": "01/01/2025", "trang_thai": "Hết hiệu lực",
        "thay_the": "Bị thay thế bởi Thông tư 79/2025/TT-BTC", "chuyen_tiep": "Áp dụng giai đoạn chuyển giao 2024-2025",
        "tags": "ALL, DAU_THAU, E_HSMT, TV-01, TV-02, TV-03, TV-04, TV-05, TV-06, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Đấu thầu qua mạng", "loai_vb": "Thông tư", "so_hieu": "79/2025/TT-BTC",
        "trich_yeu": "Hướng dẫn việc cung cấp, đăng tải thông tin về đấu thầu và mẫu hồ sơ đấu thầu trên Hệ thống mạng đấu thầu quốc gia", "co_quan": "Bộ Tài chính",
        "ngay_bh": "20/10/2025", "ngay_hl": "01/01/2026", "trang_thai": "Đang có hiệu lực",
        "thay_the": "Thay thế Thông tư 06/2024/TT-BKHĐT và Thông tư 22/2024/TT-BKHĐT", "chuyen_tiep": "Bộ mẫu E-HSMT chuẩn áp dụng bắt buộc hiện hành",
        "tags": "ALL, DAU_THAU, E_HSMT, TV-01, TV-02, TV-03, TV-04, TV-05, TV-06, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Đấu thầu qua mạng", "loai_vb": "Thông tư", "so_hieu": "07/2024/TT-BKHĐT",
        "trich_yeu": "Quy định chi tiết mẫu hồ sơ yêu cầu, báo cáo đánh giá, báo cáo thẩm định, kiểm tra, giám sát hoạt động đấu thầu", "co_quan": "Bộ Kế hoạch và Đầu tư",
        "ngay_bh": "26/04/2024", "ngay_hl": "15/06/2024", "trang_thai": "Hết hiệu lực",
        "thay_the": "Bị thay thế bởi Thông tư 23/2024/TT-BKHĐT và Thông tư 80/2025/TT-BTC", "chuyen_tiep": "Áp dụng giai đoạn đầu 2024",
        "tags": "ALL, DAU_THAU, E_HSMT, TV-01, TV-02, TV-03, TV-04, TV-05, TV-06, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Đấu thầu qua mạng", "loai_vb": "Thông tư", "so_hieu": "23/2024/TT-BKHĐT",
        "trich_yeu": "Quy định chi tiết mẫu hồ sơ yêu cầu, báo cáo đánh giá, báo cáo thẩm định, kiểm tra, báo cáo tình hình thực hiện hoạt động đấu thầu", "co_quan": "Bộ Kế hoạch và Đầu tư",
        "ngay_bh": "18/11/2024", "ngay_hl": "01/01/2025", "trang_thai": "Hết hiệu lực",
        "thay_the": "Bị thay thế bởi Thông tư 80/2025/TT-BTC", "chuyen_tiep": "Áp dụng giai đoạn cuối 2024",
        "tags": "ALL, DAU_THAU, E_HSMT, TV-01, TV-02, TV-03, TV-04, TV-05, TV-06, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Đấu thầu qua mạng", "loai_vb": "Thông tư", "so_hieu": "80/2025/TT-BTC",
        "trich_yeu": "Quy định chi tiết mẫu hồ sơ yêu cầu, báo cáo đánh giá, báo cáo thẩm định, kiểm tra, báo cáo tình hình thực hiện hoạt động đấu thầu", "co_quan": "Bộ Tài chính",
        "ngay_bh": "20/10/2025", "ngay_hl": "01/01/2026", "trang_thai": "Đang có hiệu lực",
        "thay_the": "Thay thế Thông tư 07/2024/TT-BKHĐT và Thông tư 23/2024/TT-BKHĐT", "chuyen_tiep": "Bộ mẫu HSYC, Báo cáo đánh giá, Thẩm định chỉ định thầu hiện hành",
        "tags": "ALL, DAU_THAU, E_HSMT, TV-01, TV-02, TV-03, TV-04, TV-05, TV-06, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Đấu thầu qua mạng", "loai_vb": "Thông tư", "so_hieu": "15/2024/TT-BKHĐT",
        "trich_yeu": "Quy định mẫu hồ sơ đấu thầu lựa chọn nhà đầu tư thực hiện dự án PPP, dự án đầu tư kinh doanh; cung cấp, đăng tải thông tin trên Hệ thống mạng đấu thầu quốc gia", "co_quan": "Bộ Kế hoạch và Đầu tư",
        "ngay_bh": "30/09/2024", "ngay_hl": "30/09/2024", "trang_thai": "Hết hiệu lực",
        "thay_the": "Bị thay thế bởi Thông tư 98/2025/TT-BTC", "chuyen_tiep": "Áp dụng giai đoạn 2024",
        "tags": "DAU_THAU, DAU_TU_KINH_DOANH, PPP", "link_iv": ""
    },
    {
        "linh_vuc": "Đấu thầu qua mạng", "loai_vb": "Thông tư", "so_hieu": "98/2025/TT-BTC",
        "trich_yeu": "Quy định mẫu hồ sơ đấu thầu lựa chọn nhà đầu tư thực hiện dự án đầu tư theo phương thức đối tác công tư, dự án đầu tư kinh doanh; cung cấp, đăng tải thông tin về đầu tư theo phương thức đối tác công tư, đấu thầu lựa chọn nhà đầu tư trên Hệ thống mạng đấu thầu quốc gia", "co_quan": "Bộ Tài chính",
        "ngay_bh": "15/11/2025", "ngay_hl": "01/01/2026", "trang_thai": "Đang có hiệu lực",
        "thay_the": "Thay thế Thông tư 15/2024/TT-BKHĐT", "chuyen_tiep": "Quy định mẫu đấu thầu dự án PPP và kinh doanh hiện hành",
        "tags": "DAU_THAU, DAU_TU_KINH_DOANH, PPP", "link_iv": ""
    },
    {
        "linh_vuc": "Quản lý Chi phí & Dự toán", "loai_vb": "Nghị định", "so_hieu": "10/2021/NĐ-CP",
        "trich_yeu": "Về quản lý chi phí đầu tư xây dựng", "co_quan": "Chính phủ",
        "ngay_bh": "09/02/2021", "ngay_hl": "09/02/2021", "trang_thai": "Hết hiệu lực",
        "thay_the": "Bị thay thế bởi Nghị định 206/2026/NĐ-CP", "chuyen_tiep": "Dự toán duyệt trước 2026 tiếp tục áp dụng theo phê duyệt",
        "tags": "ALL, DU_TOAN, QUAN_LY_CHI_PHI, TV-01, TV-02, TV-03, TV-04, TV-05, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Quản lý Chi phí & Dự toán", "loai_vb": "Nghị định", "so_hieu": "206/2026/NĐ-CP",
        "trich_yeu": "Quy định chi tiết về quản lý chi phí đầu tư xây dựng", "co_quan": "Chính phủ",
        "ngay_bh": "25/05/2026", "ngay_hl": "01/07/2026", "trang_thai": "Đang có hiệu lực",
        "thay_the": "Thay thế Nghị định 10/2021/NĐ-CP", "chuyen_tiep": "Căn cứ pháp lý then chốt về quản lý chi phí và dự toán hiện hành",
        "tags": "ALL, DU_TOAN, QUAN_LY_CHI_PHI, TV-01, TV-02, TV-03, TV-04, TV-05, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Quản lý Chi phí & Dự toán", "loai_vb": "Thông tư", "so_hieu": "11/2021/TT-BXD",
        "trich_yeu": "Hướng dẫn một số nội dung xác định và quản lý chi phí đầu tư xây dựng", "co_quan": "Bộ Xây dựng",
        "ngay_bh": "31/08/2021", "ngay_hl": "15/10/2021", "trang_thai": "Đang có hiệu lực",
        "thay_the": "None", "chuyen_tiep": "Phương pháp lập đơn giá xây dựng và tổng mức đầu tư",
        "tags": "ALL, DU_TOAN, QUAN_LY_CHI_PHI, TV-01, TV-02, TV-03, TV-04, TV-05, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Quản lý Chi phí & Dự toán", "loai_vb": "Thông tư", "so_hieu": "12/2021/TT-BXD",
        "trich_yeu": "Ban hành định mức xây dựng (Định mức dự toán, định mức chi phí tư vấn và QLDA)", "co_quan": "Bộ Xây dựng",
        "ngay_bh": "31/08/2021", "ngay_hl": "15/10/2021", "trang_thai": "Hết hiệu lực",
        "thay_the": "Bị thay thế bởi Thông tư 38/2026/TT-BXD", "chuyen_tiep": "Bộ định mức gốc tính chi phí tư vấn và xây lắp giai đoạn 2021-2026",
        "tags": "ALL, DINH_MUC, DU_TOAN, TV-01, TV-02, TV-03, TV-04, TV-05, TV-06, TV-08, TV-09, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Quản lý Chi phí & Dự toán", "loai_vb": "Thông tư", "so_hieu": "13/2021/TT-BXD",
        "trich_yeu": "Hướng dẫn phương pháp xác định các chỉ tiêu kinh tế kỹ thuật và đo bóc khối lượng công trình", "co_quan": "Bộ Xây dựng",
        "ngay_bh": "31/08/2021", "ngay_hl": "15/10/2021", "trang_thai": "Đang có hiệu lực",
        "thay_the": "None", "chuyen_tiep": "Quy tắc đo bóc khối lượng từ bản vẽ thiết kế BVTC",
        "tags": "DO_BOC_KHOI_LUONG, DU_TOAN, TV-04, TV-05", "link_iv": ""
    },
    {
        "linh_vuc": "Quản lý Chi phí & Dự toán", "loai_vb": "Thông tư", "so_hieu": "14/2023/TT-BXD",
        "trich_yeu": "Sửa đổi, bổ sung một số điều của Thông tư số 11/2021/TT-BXD ngày 31 tháng 8 năm 2021 hướng dẫn một số nội dung xác định và quản lý chi phí đầu tư xây dựng", "co_quan": "Bộ Xây dựng",
        "ngay_bh": "29/12/2023", "ngay_hl": "15/02/2024", "trang_thai": "Đang có hiệu lực",
        "thay_the": "None", "chuyen_tiep": "Áp dụng định mức chi phí tư vấn lập dự án và thẩm tra",
        "tags": "ALL, DU_TOAN, QUAN_LY_CHI_PHI, TV-01, TV-02, TV-03, TV-04, TV-05, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Quản lý Chi phí & Dự toán", "loai_vb": "Thông tư", "so_hieu": "01/2025/TT-BXD",
        "trich_yeu": "Sửa đổi, bổ sung một số điều của Thông tư số 13/2021/TT-BXD, Thông tư số 11/2021/TT-BXD, Thông tư số 14/2023/TT-BXD", "co_quan": "Bộ Xây dựng",
        "ngay_bh": "15/01/2025", "ngay_hl": "01/03/2025", "trang_thai": "Đang có hiệu lực",
        "thay_the": "None", "chuyen_tiep": "Cập nhật phương pháp xác định chi phí và chỉ tiêu kinh tế kỹ thuật mới",
        "tags": "ALL, DU_TOAN, QUAN_LY_CHI_PHI, TV-01, TV-02, TV-03, TV-04, TV-05, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Quản lý Chi phí & Dự toán", "loai_vb": "Thông tư", "so_hieu": "09/2024/TT-BXD",
        "trich_yeu": "Sửa đổi, bổ sung một số điều của Thông tư số 12/2021/TT-BXD ngày 31 tháng 8 năm 2021 ban hành định mức xây dựng", "co_quan": "Bộ Xây dựng",
        "ngay_bh": "30/08/2024", "ngay_hl": "15/10/2024", "trang_thai": "Hết hiệu lực",
        "thay_the": "Bị tích hợp và thay thế bởi Thông tư 38/2026/TT-BXD", "chuyen_tiep": "Cập nhật định mức nhân công, ca máy giai đoạn 2024-2026",
        "tags": "ALL, DINH_MUC, DU_TOAN, TV-01, TV-02, TV-03, TV-04, TV-05, TV-06, TV-08, TV-09, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Quản lý Chi phí & Dự toán", "loai_vb": "Thông tư", "so_hieu": "38/2026/TT-BXD",
        "trich_yeu": "Ban hành định mức xây dựng", "co_quan": "Bộ Xây dựng",
        "ngay_bh": "15/06/2026", "ngay_hl": "01/08/2026", "trang_thai": "Đang có hiệu lực",
        "thay_the": "Thay thế Thông tư 12/2021/TT-BXD và Thông tư 09/2024/TT-BXD", "chuyen_tiep": "Hệ thống định mức dự toán xây dựng hiện hành",
        "tags": "ALL, DINH_MUC, DU_TOAN, TV-01, TV-02, TV-03, TV-04, TV-05, TV-06, TV-08, TV-09, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Quản lý Chi phí & Dự toán", "loai_vb": "Quyết định", "so_hieu": "510/QĐ-BXD",
        "trich_yeu": "Công bố Suất vốn đầu tư xây dựng công trình và giá chuẩn nhà, công trình xây dựng", "co_quan": "Bộ Xây dựng",
        "ngay_bh": "19/05/2023", "ngay_hl": "19/05/2023", "trang_thai": "Hết hiệu lực",
        "thay_the": "Bị thay thế bởi Quyết định 425/QĐ-BXD", "chuyen_tiep": "Suất vốn đầu tư năm 2022-2023",
        "tags": "SUAT_VON_DAU_TU, TMDT, TV-01, TV-02, TV-03, TV-04", "link_iv": ""
    },
    {
        "linh_vuc": "Quản lý Chi phí & Dự toán", "loai_vb": "Quyết định", "so_hieu": "425/QĐ-BXD",
        "trich_yeu": "Công bố suất vốn đầu tư xây dựng và giá xây dựng tổng hợp bộ phận kết cấu công trình năm 2025", "co_quan": "Bộ Xây dựng",
        "ngay_bh": "25/04/2025", "ngay_hl": "25/04/2025", "trang_thai": "Hết hiệu lực",
        "thay_the": "Thay thế Quyết định 510/QĐ-BXD", "chuyen_tiep": "Suất vốn đầu tư tính Tổng mức đầu tư và khái toán",
        "tags": "SUAT_VON_DAU_TU, TMDT, TV-01, TV-02, TV-03, TV-04", "link_iv": ""
    },
    {
        "linh_vuc": "Chất lượng & Nghiệm thu", "loai_vb": "Nghị định", "so_hieu": "06/2021/NĐ-CP",
        "trich_yeu": "Quy định chi tiết về quản lý chất lượng, thi công xây dựng và bảo trì công trình xây dựng", "co_quan": "Chính phủ",
        "ngay_bh": "26/01/2021", "ngay_hl": "26/01/2021", "trang_thai": "Đang có hiệu lực",
        "thay_the": "None", "chuyen_tiep": "Quy định nền tảng về quản lý chất lượng và nghiệm thu công trình",
        "tags": "CHAT_LUONG, NGHIEM_THU, TV-01, TV-02, TV-04, TV-05, TV-07, TV-08, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Chất lượng & Nghiệm thu", "loai_vb": "Nghị định", "so_hieu": "207/2026/NĐ-CP",
        "trich_yeu": "Quy định chi tiết một số điều của Luật Xây dựng về quản lý chất lượng, thi công xây dựng và bảo trì công trình xây dựng", "co_quan": "Chính phủ",
        "ngay_bh": "26/05/2026", "ngay_hl": "01/07/2026", "trang_thai": "Đang có hiệu lực",
        "thay_the": "Cập nhật và hoàn thiện Nghị định 06/2021/NĐ-CP theo Luật Xây dựng mới", "chuyen_tiep": "Quy chuẩn quản lý chất lượng công trình xây dựng hiện hành",
        "tags": "ALL, CHAT_LUONG, NGHIEM_THU, XD-01, TV-08, TV-07", "link_iv": ""
    },
    {
        "linh_vuc": "Chất lượng & Nghiệm thu", "loai_vb": "Thông tư", "so_hieu": "10/2021/TT-BXD",
        "trich_yeu": "Hướng dẫn một số điều của Nghị định số 06/2021/NĐ-CP và Nghị định số 44/2016/NĐ-CP", "co_quan": "Bộ Xây dựng",
        "ngay_bh": "25/08/2021", "ngay_hl": "15/10/2021", "trang_thai": "Đang có hiệu lực",
        "thay_the": "None", "chuyen_tiep": "Mẫu nhật ký thi công, biên bản nghiệm thu giai đoạn và hoàn thành",
        "tags": "CHAT_LUONG, NGHIEM_THU, TV-01, TV-02, TV-04, TV-05, TV-07, TV-08, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Chất lượng & Nghiệm thu", "loai_vb": "Thông tư", "so_hieu": "32/2026/TT-BXD",
        "trich_yeu": "Quy định chi tiết một số điều của Nghị định số 207/2026/NĐ-CP quy định chi tiết một số điều của Luật Xây dựng về quản lý chất lượng, thi công xây dựng và bảo trì công trình xây dựng", "co_quan": "Bộ Xây dựng",
        "ngay_bh": "20/06/2026", "ngay_hl": "01/08/2026", "trang_thai": "Đang có hiệu lực",
        "thay_the": "Hướng dẫn Nghị định 207/2026/NĐ-CP", "chuyen_tiep": "Biểu mẫu quản lý chất lượng và kiểm tra công tác nghiệm thu mới nhất",
        "tags": "ALL, CHAT_LUONG, NGHIEM_THU, XD-01, TV-08", "link_iv": ""
    },
    {
        "linh_vuc": "PCCC & Tiêu chuẩn Kỹ thuật", "loai_vb": "Quy chuẩn", "so_hieu": "QCVN 06:2022/BXD & Sửa đổi 1:2023",
        "trich_yeu": "Quy chuẩn kỹ thuật quốc gia về An toàn cháy cho nhà và công trình", "co_quan": "Bộ Xây dựng",
        "ngay_bh": "16/10/2023", "ngay_hl": "01/12/2023", "trang_thai": "Đang có hiệu lực",
        "thay_the": "QCVN 06:2021/BXD", "chuyen_tiep": "Hồ sơ thiết kế BVTC phải tuân thủ đúng yêu cầu ngăn cháy, thoát nạn",
        "tags": "PCCC, THIET_KE, TV-04, TV-05, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "PCCC & Tiêu chuẩn Kỹ thuật", "loai_vb": "Nghị định", "so_hieu": "136/2020/NĐ-CP",
        "trich_yeu": "Quy định chi tiết một số điều và biện pháp thi hành Luật Phòng cháy và chữa cháy", "co_quan": "Chính phủ",
        "ngay_bh": "24/11/2020", "ngay_hl": "10/01/2021", "trang_thai": "Hết hiệu lực",
        "thay_the": "Bị thay thế bởi Nghị định 105/2025/NĐ-CP", "chuyen_tiep": "Áp dụng giai đoạn 2020-2025",
        "tags": "PCCC, TV-02, TV-03, TV-04, TV-05, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "PCCC & Tiêu chuẩn Kỹ thuật", "loai_vb": "Nghị định", "so_hieu": "105/2025/NĐ-CP",
        "trich_yeu": "Quy định chi tiết một số điều và biện pháp thi hành Luật Phòng cháy, chữa cháy và cứu nạn, cứu hộ", "co_quan": "Chính phủ",
        "ngay_bh": "15/05/2025", "ngay_hl": "01/07/2025", "trang_thai": "Đang có hiệu lực",
        "thay_the": "Thay thế Nghị định 136/2020/NĐ-CP và Nghị định 50/2024/NĐ-CP", "chuyen_tiep": "Quy định thẩm duyệt thiết kế và nghiệm thu PCCC hiện hành",
        "tags": "ALL, PCCC, THIET_KE, TV-04, TV-05, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "PCCC & Tiêu chuẩn Kỹ thuật", "loai_vb": "Nghị định", "so_hieu": "50/2024/NĐ-CP",
        "trich_yeu": "Sửa đổi, bổ sung một số điều của Nghị định số 136/2020/NĐ-CP và Nghị định số 83/2017/NĐ-CP về PCCC và cứu nạn, cứu hộ", "co_quan": "Chính phủ",
        "ngay_bh": "10/05/2024", "ngay_hl": "15/05/2024", "trang_thai": "Hết hiệu lực",
        "thay_the": "Bị thay thế bởi Nghị định 105/2025/NĐ-CP", "chuyen_tiep": "Phân cấp thẩm duyệt PCCC giai đoạn 2024-2025",
        "tags": "PCCC, TV-02, TV-03, TV-04, TV-05, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Hợp đồng xây dựng", "loai_vb": "Nghị định", "so_hieu": "37/2015/NĐ-CP & 50/2021/NĐ-CP",
        "trich_yeu": "Quy định chi tiết về hợp đồng xây dựng và sửa đổi, bổ sung Nghị định 37/2015/NĐ-CP", "co_quan": "Chính phủ",
        "ngay_bh": "01/04/2021", "ngay_hl": "01/04/2021", "trang_thai": "Hết hiệu lực",
        "thay_the": "Bị thay thế bởi Nghị định 210/2026/NĐ-CP", "chuyen_tiep": "Hợp đồng ký trước 2026 thực hiện theo thỏa thuận đã ký",
        "tags": "HOP_DONG, XD-01, TV-04, TV-05, TV-06, TV-07, TV-08, TV-09, PTV-01", "link_iv": ""
    },
    {
        "linh_vuc": "Hợp đồng xây dựng", "loai_vb": "Nghị định", "so_hieu": "210/2026/NĐ-CP",
        "trich_yeu": "Quy định chi tiết và hướng dẫn thi hành một số điều của Luật Xây dựng về hợp đồng xây dựng", "co_quan": "Chính phủ",
        "ngay_bh": "02/06/2026", "ngay_hl": "01/07/2026", "trang_thai": "Đang có hiệu lực",
        "thay_the": "Thay thế Nghị định 37/2015/NĐ-CP và Nghị định 50/2021/NĐ-CP", "chuyen_tiep": "Quy định tạm ứng, bảo lãnh thực hiện hợp đồng và thanh quyết toán hiện hành",
        "tags": "ALL, HOP_DONG, XD-01, TV-04, TV-05, TV-06, TV-07, TV-08, TV-09, PTV-01", "link_iv": ""
    },
    {
        "linh_vuc": "Hợp đồng xây dựng", "loai_vb": "Thông tư", "so_hieu": "02/2023/TT-BXD",
        "trich_yeu": "Hướng dẫn một số nội dung về hợp đồng xây dựng (Mẫu hợp đồng thi công và tư vấn)", "co_quan": "Bộ Xây dựng",
        "ngay_bh": "03/03/2023", "ngay_hl": "20/04/2023", "trang_thai": "Đang có hiệu lực",
        "thay_the": "Thay thế Thông tư 09/2016/TT-BXD và Thông tư 08/2016/TT-BXD", "chuyen_tiep": "Mẫu hợp đồng áp dụng bắt buộc cho vốn nhà nước",
        "tags": "HOP_DONG, XD-01, TV-04, TV-08", "link_iv": ""
    },
    {
        "linh_vuc": "Tiêu chuẩn Kỹ thuật", "loai_vb": "Tiêu chuẩn", "so_hieu": "TCVN 9393:2012",
        "trich_yeu": "Cọc - Phương pháp thử nghiệm hiện trường bằng tải trọng tĩnh ép dọc trục", "co_quan": "Bộ Khoa học và Công nghệ",
        "ngay_bh": "28/12/2012", "ngay_hl": "28/12/2012", "trang_thai": "Đang có hiệu lực",
        "thay_the": "None", "chuyen_tiep": "Căn cứ kỹ thuật duy nhất cho gói thầu Thí nghiệm nén tĩnh cọc TV-07",
        "tags": "TV-07, THI_NGHIEM_COC, KIEM_DINH", "link_iv": ""
    },
    {
        "linh_vuc": "Bảo hiểm công trình", "loai_vb": "Luật", "so_hieu": "08/2022/QH15",
        "trich_yeu": "Luật Kinh doanh bảo hiểm năm 2022", "co_quan": "Quốc hội",
        "ngay_bh": "16/06/2022", "ngay_hl": "01/01/2023", "trang_thai": "Đang có hiệu lực",
        "thay_the": "None", "chuyen_tiep": "Căn cứ pháp lý gói thầu Bảo hiểm công trình PTV-01",
        "tags": "PTV-01, BAO_HIEM", "link_iv": ""
    },
    {
        "linh_vuc": "Bảo hiểm công trình", "loai_vb": "Nghị định", "so_hieu": "67/2023/NĐ-CP",
        "trich_yeu": "Quy định về bảo hiểm bắt buộc trong hoạt động đầu tư xây dựng, bảo hiểm cháy nổ bắt buộc", "co_quan": "Chính phủ",
        "ngay_bh": "06/09/2023", "ngay_hl": "06/09/2023", "trang_thai": "Đang có hiệu lực",
        "thay_the": "Thay thế Nghị định 119/2015/NĐ-CP và Nghị định 20/2020/NĐ-CP", "chuyen_tiep": "Biểu phí bảo hiểm công trình xây dựng áp dụng cho gói PTV-01",
        "tags": "PTV-01, BAO_HIEM, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Bảo hiểm công trình", "loai_vb": "Nghị định", "so_hieu": "220/2026/NĐ-CP",
        "trich_yeu": "Sửa đổi, bổ sung một số điều của Nghị định số 67/2023/NĐ-CP quy định về bảo hiểm bắt buộc trách nhiệm dân sự của chủ xe cơ giới, bảo hiểm cháy, nổ bắt buộc, bảo hiểm bắt buộc trong hoạt động đầu tư xây dựng", "co_quan": "Chính phủ",
        "ngay_bh": "12/06/2026", "ngay_hl": "01/08/2026", "trang_thai": "Đang có hiệu lực",
        "thay_the": "None", "chuyen_tiep": "Cập nhật mức khấu trừ và biểu phí bảo hiểm công trình mới nhất",
        "tags": "ALL, PTV-01, BAO_HIEM, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Bảo hiểm công trình", "loai_vb": "Nghị định", "so_hieu": "119/2015/NĐ-CP",
        "trich_yeu": "Quy định bảo hiểm bắt buộc trong hoạt động đầu tư xây dựng", "co_quan": "Chính phủ",
        "ngay_bh": "13/11/2015", "ngay_hl": "10/02/2016", "trang_thai": "Hết hiệu lực",
        "thay_the": "Bị thay thế bởi Nghị định 67/2023/NĐ-CP", "chuyen_tiep": "Áp dụng cho hợp đồng bảo hiểm ký trước 06/09/2023",
        "tags": "PTV-01, LICHSU", "link_iv": ""
    },
    {
        "linh_vuc": "Kiểm toán độc lập", "loai_vb": "Luật", "so_hieu": "67/2011/QH12",
        "trich_yeu": "Luật Kiểm toán độc lập", "co_quan": "Quốc hội",
        "ngay_bh": "29/03/2011", "ngay_hl": "01/01/2012", "trang_thai": "Đang có hiệu lực",
        "thay_the": "None", "chuyen_tiep": "Căn cứ thực hiện gói thầu Kiểm toán độc lập TV-09",
        "tags": "TV-09, KIEM_TOAN", "link_iv": ""
    },
    {
        "linh_vuc": "Kiểm toán độc lập", "loai_vb": "Thông tư", "so_hieu": "67/2015/TT-BTC",
        "trich_yeu": "Chuẩn mực kiểm toán Việt Nam số 1000 (VSA 1000) - Kiểm toán báo cáo quyết toán dự án hoàn thành", "co_quan": "Bộ Tài chính",
        "ngay_bh": "08/05/2015", "ngay_hl": "01/01/2016", "trang_thai": "Đang có hiệu lực",
        "thay_the": "None", "chuyen_tiep": "Chuẩn mực kiểm toán áp dụng cho gói TV-09",
        "tags": "TV-09, KIEM_TOAN", "link_iv": ""
    },
    {
        "linh_vuc": "Quyết toán vốn dự án", "loai_vb": "Luật", "so_hieu": "58/2024/QH15",
        "trich_yeu": "Luật Đầu tư công năm 2024 (Đẩy mạnh phân cấp, phân quyền, tách bồi thường GPMB)", "co_quan": "Quốc hội",
        "ngay_bh": "29/11/2024", "ngay_hl": "01/01/2025", "trang_thai": "Đang có hiệu lực",
        "thay_the": "Thay thế Luật Đầu tư công 39/2019/QH14", "chuyen_tiep": "Quy định trình tự phê duyệt chủ trương, kế hoạch vốn và quyết toán",
        "tags": "ALL, DAU_TU_CONG, CHU_TRUONG, TV-01, TV-02, TV-03, TV-09", "link_iv": ""
    },
    {
        "linh_vuc": "Quyết toán vốn dự án", "loai_vb": "Luật", "so_hieu": "39/2019/QH14",
        "trich_yeu": "Luật Đầu tư công năm 2019", "co_quan": "Quốc hội",
        "ngay_bh": "13/06/2019", "ngay_hl": "01/01/2020", "trang_thai": "Hết hiệu lực",
        "thay_the": "Bị thay thế bởi Luật Đầu tư công 58/2024/QH15", "chuyen_tiep": "Áp dụng cho dự án đã duyệt chủ trương trước 2025",
        "tags": "ALL, DAU_TU_CONG, CHU_TRUONG, TV-01, TV-02, TV-03, TV-09", "link_iv": ""
    },
    {
        "linh_vuc": "Quyết toán vốn dự án", "loai_vb": "Nghị định", "so_hieu": "99/2021/NĐ-CP",
        "trich_yeu": "Quy định về quản lý, thanh toán, quyết toán dự án sử dụng vốn đầu tư công", "co_quan": "Chính phủ",
        "ngay_bh": "11/11/2021", "ngay_hl": "01/01/2022", "trang_thai": "Hết hiệu lực",
        "thay_the": "Thay thế Nghị định 77/2015/NĐ-CP và Nghị định 120/2018/NĐ-CP về quyết toán vốn ĐTC", "chuyen_tiep": "Hồ sơ thanh toán, quyết toán vốn đầu tư công giai đoạn 2022-2025",
        "tags": "ALL, QUYET_TOAN, TAI_CHINH, TV-09, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Quyết toán vốn dự án", "loai_vb": "Thông tư", "so_hieu": "24/2024/TT-BTC",
        "trich_yeu": "Hướng dẫn Chế độ kế toán Hành chính, sự nghiệp (Hạch toán tài sản và vốn dự án)", "co_quan": "Bộ Tài chính",
        "ngay_bh": "17/04/2024", "ngay_hl": "01/01/2025", "trang_thai": "Đang có hiệu lực",
        "thay_the": "Thay thế Thông tư 107/2017/TT-BTC", "chuyen_tiep": "Hạch toán sổ sách tài sản và vốn đầu tư hoàn thành hiện hành",
        "tags": "ALL, QUYET_TOAN, TAI_CHINH, TV-09, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Quốc phòng & Doanh trại", "loai_vb": "Thông tư", "so_hieu": "150/2018/TT-BQP",
        "trich_yeu": "Quy định về tiêu chuẩn, định mức sử dụng máy móc, thiết bị văn phòng phổ biến thuộc phạm vi quản lý của Bộ Quốc phòng", "co_quan": "Bộ Quốc phòng",
        "ngay_bh": "11/10/2018", "ngay_hl": "26/11/2018", "trang_thai": "Đang có hiệu lực",
        "thay_the": "Thay thế Quyết định 162/2002/QĐ-BQP", "chuyen_tiep": "Tiêu chuẩn định mức máy móc, thiết bị làm việc của cán bộ sĩ quan BQP",
        "tags": "BQP, DOANH_TRAI, TV-01, TV-02, TV-04, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Quốc phòng & Doanh trại", "loai_vb": "Thông tư", "so_hieu": "128/2021/TT-BQP",
        "trich_yeu": "Quy định phân cấp, ủy quyền quyết định chủ trương đầu tư và dự án đầu tư công trong Bộ Quốc phòng", "co_quan": "Bộ Quốc phòng",
        "ngay_bh": "06/10/2021", "ngay_hl": "20/11/2021", "trang_thai": "Hết hiệu lực",
        "thay_the": "Bị thay thế bởi Thông tư 102/2026/TT-BQP", "chuyen_tiep": "Áp dụng phân cấp thẩm quyền đầu tư BQP giai đoạn 2021-2026",
        "tags": "ALL, BQP, PHAN_CAP, QLDA, TV-01, TV-02, TV-03, TV-04, TV-05, TV-08, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Quốc phòng & Doanh trại", "loai_vb": "Thông tư", "so_hieu": "174/2021/TT-BQP",
        "trich_yeu": "Quy định về quản lý chất lượng, thi công xây dựng và bảo trì công trình xây dựng trong Bộ Quốc phòng", "co_quan": "Bộ Quốc phòng",
        "ngay_bh": "27/12/2021", "ngay_hl": "12/02/2022", "trang_thai": "Đang có hiệu lực",
        "thay_the": "Được sửa đổi, bổ sung bởi Thông tư 24/2025/TT-BQP", "chuyen_tiep": "Quy chuẩn nghiệm thu và quản lý chất lượng công trình quân sự",
        "tags": "CHAT_LUONG, NGHIEM_THU, TV-01, TV-02, TV-04, TV-05, TV-07, TV-08, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Quốc phòng & Doanh trại", "loai_vb": "Thông tư", "so_hieu": "94/2024/TT-BQP",
        "trich_yeu": "Quy định chi tiết một số điều của Luật Nhà ở áp dụng trong Bộ Quốc phòng (Mẫu giấy tờ nhà ở công vụ và dự án nhà ở LLVT)", "co_quan": "Bộ Quốc phòng",
        "ngay_bh": "11/11/2024", "ngay_hl": "26/12/2024", "trang_thai": "Đang có hiệu lực",
        "thay_the": "None", "chuyen_tiep": "Áp dụng cho các dự án đầu tư xây dựng nhà ở cho lực lượng vũ trang thuộc BQP",
        "tags": "BQP, DOANH_TRAI, TV-01, TV-02, TV-04, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Quốc phòng & Doanh trại", "loai_vb": "Thông tư", "so_hieu": "73/2023/TT-BQP",
        "trich_yeu": "Sửa đổi, bổ sung một số điều của Thông tư số 128/2021/TT-BQP ngày 01/10/2021 về quy định phân cấp, ủy quyền quyết định chủ trương đầu tư và dự án đầu tư công trong BQP", "co_quan": "Bộ Quốc phòng",
        "ngay_bh": "05/10/2023", "ngay_hl": "20/11/2023", "trang_thai": "Hết hiệu lực",
        "thay_the": "Bị thay thế bởi Thông tư 102/2026/TT-BQP", "chuyen_tiep": "Cập nhật phân cấp đầu tư BQP giai đoạn 2023-2026",
        "tags": "ALL, BQP, PHAN_CAP, QLDA, TV-01, TV-02, TV-03, TV-04, TV-05, TV-08, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Quốc phòng & Doanh trại", "loai_vb": "Thông tư", "so_hieu": "120/2024/TT-BQP",
        "trich_yeu": "Sửa đổi, bổ sung một số điều của Thông tư số 128/2021/TT-BQP về phân cấp quản lý và thực hiện dự án đầu tư công trong Bộ Quốc phòng", "co_quan": "Bộ Quốc phòng",
        "ngay_bh": "26/12/2024", "ngay_hl": "10/02/2025", "trang_thai": "Hết hiệu lực",
        "thay_the": "Bị thay thế bởi Thông tư 102/2026/TT-BQP", "chuyen_tiep": "Phân cấp phê duyệt thiết kế, dự toán BQP giai đoạn 2024-2026",
        "tags": "ALL, BQP, PHAN_CAP, QLDA, TV-01, TV-02, TV-03, TV-04, TV-05, TV-08, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Quốc phòng & Doanh trại", "loai_vb": "Thông tư", "so_hieu": "24/2025/TT-BQP",
        "trich_yeu": "Sửa đổi, bổ sung một số điều của Thông tư số 174/2021/TT-BQP về quản lý chất lượng, thi công xây dựng và bảo trì công trình xây dựng trong Bộ Quốc phòng", "co_quan": "Bộ Quốc phòng",
        "ngay_bh": "06/05/2025", "ngay_hl": "20/06/2025", "trang_thai": "Đang có hiệu lực",
        "thay_the": "Sửa đổi, bổ sung Thông tư 174/2021/TT-BQP về quản lý chất lượng công trình BQP", "chuyen_tiep": "Quy chuẩn kiểm tra công tác nghiệm thu công trình quân sự đặc thù hiện hành",
        "tags": "CHAT_LUONG, NGHIEM_THU, TV-01, TV-02, TV-04, TV-05, TV-07, TV-08, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Quốc phòng & Doanh trại", "loai_vb": "Thông tư", "so_hieu": "101/2026/TT-BQP",
        "trich_yeu": "Quy định chi tiết và biện pháp thực hiện một số nội dung Luật Xây dựng thuộc phạm vi quản lý của Bộ Quốc phòng", "co_quan": "Bộ Quốc phòng",
        "ngay_bh": "09/07/2026", "ngay_hl": "09/07/2026", "trang_thai": "Đang có hiệu lực",
        "thay_the": "None", "chuyen_tiep": "Áp dụng cho các dự án đầu tư xây dựng công trình trong toàn Bộ Quốc phòng",
        "tags": "ALL, BQP, QLDA, XD-01, TOAN_QUAN", "link_iv": ""
    },
    {
        "linh_vuc": "Quốc phòng & Doanh trại", "loai_vb": "Thông tư", "so_hieu": "102/2026/TT-BQP",
        "trich_yeu": "Quy định và hướng dẫn về lập, thẩm định, quyết định, phân cấp quyết định chủ trương đầu tư, dự án đầu tư trong Bộ Quốc phòng", "co_quan": "Bộ Quốc phòng",
        "ngay_bh": "17/07/2026", "ngay_hl": "17/07/2026", "trang_thai": "Đang có hiệu lực",
        "thay_the": "Thay thế Thông tư 128/2021/TT-BQP, Thông tư 73/2023/TT-BQP và Thông tư 120/2024/TT-BQP", "chuyen_tiep": "Văn bản xương sống về phân cấp, ủy quyền quyết định đầu tư và dự án đầu tư công mới nhất trong BQP",
        "tags": "ALL, BQP, PHAN_CAP, QLDA, TV-01, TV-02, TV-03, TV-04, TV-05, TV-08, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Quốc phòng & Doanh trại", "loai_vb": "Quyết định", "so_hieu": "35/QĐ-TTg",
        "trich_yeu": "Ban hành Danh mục bí mật Nhà nước trong lĩnh vực Quốc phòng", "co_quan": "Thủ tướng Chính phủ",
        "ngay_bh": "11/03/2025", "ngay_hl": "11/03/2025", "trang_thai": "Đang có hiệu lực",
        "thay_the": "Quyết định số 12/QĐ-TTg", "chuyen_tiep": "Quy định bảo mật hồ sơ, tài liệu thiết kế công trình quân sự",
        "tags": "ALL, BQP, PHAN_CAP, QLDA, TV-01, TV-02, TV-03, TV-04, TV-05, TV-08, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Chi thường xuyên & Tài sản công", "loai_vb": "Luật", "so_hieu": "15/2017/QH14",
        "trich_yeu": "Luật Quản lý, sử dụng tài sản công", "co_quan": "Quốc hội",
        "ngay_bh": "21/06/2017", "ngay_hl": "01/01/2018", "trang_thai": "Đang có hiệu lực",
        "thay_the": "Luật Quản lý tài sản nhà nước 2008", "chuyen_tiep": "Chế độ quản lý, bảo dưỡng, nâng cấp và sử dụng tài sản công",
        "tags": "CHI_THUONG_XUYEN, TAI_SAN_CONG, SUA_CHUA, TV-01, TV-02, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Chi thường xuyên & Tài sản công", "loai_vb": "Nghị định", "so_hieu": "151/2017/NĐ-CP",
        "trich_yeu": "Quy định chi tiết một số điều của Luật Quản lý, sử dụng tài sản công", "co_quan": "Chính phủ",
        "ngay_bh": "26/12/2017", "ngay_hl": "01/01/2018", "trang_thai": "Hết hiệu lực",
        "thay_the": "Bị thay thế bởi Nghị định 186/2025/NĐ-CP", "chuyen_tiep": "Áp dụng phân cấp tài sản công giai đoạn 2018-2025",
        "tags": "CHI_THUONG_XUYEN, TAI_SAN_CONG, SUA_CHUA, TV-01, TV-02, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Chi thường xuyên & Tài sản công", "loai_vb": "Nghị định", "so_hieu": "186/2025/NĐ-CP",
        "trich_yeu": "Quy định chi tiết một số điều của Luật Quản lý, sử dụng tài sản công", "co_quan": "Chính phủ",
        "ngay_bh": "18/09/2025", "ngay_hl": "01/11/2025", "trang_thai": "Đang có hiệu lực",
        "thay_the": "Thay thế Nghị định 151/2017/NĐ-CP", "chuyen_tiep": "Quy định phân cấp thẩm quyền quyết định mua sắm, sửa chữa, bàn giao tài sản công hiện hành",
        "tags": "CHI_THUONG_XUYEN, TAI_SAN_CONG, SUA_CHUA, TV-01, TV-02, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Chi thường xuyên & Tài sản công", "loai_vb": "Nghị định", "so_hieu": "114/2024/NĐ-CP",
        "trich_yeu": "Sửa đổi, bổ sung một số điều của Nghị định số 151/2017/NĐ-CP quy định chi tiết một số điều của Luật Quản lý, sử dụng tài sản công", "co_quan": "Chính phủ",
        "ngay_bh": "15/09/2024", "ngay_hl": "30/10/2024", "trang_thai": "Đang có hiệu lực",
        "thay_the": "Sửa đổi, bổ sung Nghị định 151/2017/NĐ-CP về tài sản công", "chuyen_tiep": "Quy định thẩm quyền mua sắm, thuê, xử lý tài sản công",
        "tags": "CHI_THUONG_XUYEN, TAI_SAN_CONG, SUA_CHUA, TV-01, TV-02, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Chi thường xuyên & Tài sản công", "loai_vb": "Nghị định", "so_hieu": "138/2024/NĐ-CP",
        "trich_yeu": "Quy định việc lập dự toán, quản lý, sử dụng kinh phí chi thường xuyên NSNN để mua sắm tài sản, trang thiết bị; cải tạo, nâng cấp, mở rộng, xây dựng mới hạng mục công trình", "co_quan": "Chính phủ",
        "ngay_bh": "24/10/2024", "ngay_hl": "24/10/2024", "trang_thai": "Hết hiệu lực",
        "thay_the": "Bị thay thế bởi Nghị định 98/2025/NĐ-CP và Nghị định 104/2026/NĐ-CP", "chuyen_tiep": "Căn cứ giai đoạn cuối 2024",
        "tags": "CHI_THUONG_XUYEN, TAI_SAN_CONG, SUA_CHUA, TV-01, TV-02, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Chi thường xuyên & Tài sản công", "loai_vb": "Nghị định", "so_hieu": "98/2025/NĐ-CP",
        "trich_yeu": "Quy định việc lập dự toán, quản lý, sử dụng và quyết toán chi thường xuyên ngân sách nhà nước để mua sắm, sửa chữa, cải tạo, nâng cấp tài sản, trang thiết bị; chi thuê hàng hóa, dịch vụ; sửa chữa, cải tạo, nâng cấp, mở rộng, xây dựng mới hạng mục công trình trong các dự án đã đầu tư xây dựng và các nhiệm vụ cần thiết khác", "co_quan": "Chính phủ",
        "ngay_bh": "25/06/2025", "ngay_hl": "15/08/2025", "trang_thai": "Hết hiệu lực",
        "thay_the": "Bị thay thế bởi Nghị định 104/2026/NĐ-CP", "chuyen_tiep": "Áp dụng giai đoạn 2025-2026",
        "tags": "CHI_THUONG_XUYEN, TAI_SAN_CONG, SUA_CHUA, TV-01, TV-02, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Chi thường xuyên & Tài sản công", "loai_vb": "Nghị định", "so_hieu": "104/2026/NĐ-CP",
        "trich_yeu": "Quy định việc lập dự toán, quản lý, sử dụng và quyết toán chi thường xuyên để thực hiện các nhiệm vụ quy định tại Điều 40 Luật Ngân sách nhà nước", "co_quan": "Chính phủ",
        "ngay_bh": "18/06/2026", "ngay_hl": "01/08/2026", "trang_thai": "Đang có hiệu lực",
        "thay_the": "Thay thế Nghị định 138/2024/NĐ-CP và Nghị định 98/2025/NĐ-CP", "chuyen_tiep": "Căn cứ pháp lý then chốt cho các dự án sửa chữa, nâng cấp sử dụng nguồn chi thường xuyên hiện hành",
        "tags": "CHI_THUONG_XUYEN, TAI_SAN_CONG, SUA_CHUA, TV-01, TV-02, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Chi thường xuyên & Tài sản công", "loai_vb": "Thông tư", "so_hieu": "65/2021/TT-BTC",
        "trich_yeu": "Quy định về lập dự toán, phân bổ và quyết toán kinh phí bảo dưỡng, sửa chữa tài sản công", "co_quan": "Bộ Tài chính",
        "ngay_bh": "29/07/2021", "ngay_hl": "15/09/2021", "trang_thai": "Đang có hiệu lực",
        "thay_the": "Thông tư 92/2017/TT-BTC", "chuyen_tiep": "Áp dụng lập dự toán và thanh toán sửa chữa tài sản công dưới 500 triệu",
        "tags": "CHI_THUONG_XUYEN, TAI_SAN_CONG, SUA_CHUA, TV-01, TV-02, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Chất lượng & Nghiệm thu", "loai_vb": "Luật", "so_hieu": "84/2015/QH13",
        "trich_yeu": "Luật An toàn, vệ sinh lao động (Quy định an toàn lao động, phòng ngừa sự cố trên công trường xây dựng)", "co_quan": "Quốc hội",
        "ngay_bh": "25/06/2015", "ngay_hl": "01/07/2016", "trang_thai": "Đang có hiệu lực",
        "thay_the": "", "chuyen_tiep": "Căn cứ bắt buộc trong Hợp đồng thi công gói XD-01 và Giám sát an toàn gói TV-08",
        "tags": "XD-01, TV-08, AN_TOAN_LAO_DONG", "link_iv": ""
    },
    {
        "linh_vuc": "Xây dựng & Quản lý dự án", "loai_vb": "Luật", "so_hieu": "72/2020/QH14",
        "trich_yeu": "Luật Bảo vệ môi trường năm 2020", "co_quan": "Quốc hội",
        "ngay_bh": "17/11/2020", "ngay_hl": "01/01/2022", "trang_thai": "Đang có hiệu lực",
        "thay_the": "Thay thế Luật Bảo vệ môi trường 55/2014/QH13", "chuyen_tiep": "Căn cứ thực hiện thủ tục Đăng ký môi trường / ĐTM cho các hạng mục Kho xăng dầu, Bệnh xá, Bể bơi",
        "tags": "MOI_TRUONG, TV-01, TV-02, TV-03, TV-04, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Xây dựng & Quản lý dự án", "loai_vb": "Nghị định", "so_hieu": "08/2022/NĐ-CP",
        "trich_yeu": "Quy định chi tiết một số điều của Luật Bảo vệ môi trường", "co_quan": "Chính phủ",
        "ngay_bh": "10/01/2022", "ngay_hl": "10/01/2022", "trang_thai": "Đang có hiệu lực",
        "thay_the": "Được sửa đổi, bổ sung bởi Nghị định số 05/2025/NĐ-CP và Nghị định số 48/2026/NĐ-CP", "chuyen_tiep": "Quy định đối tượng và hồ sơ Đăng ký môi trường công trình (bổ trợ Nghị quyết 66.19/2026/NQ-CP)",
        "tags": "MOI_TRUONG, TV-01, TV-02, TV-03, TV-04, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Xây dựng & Quản lý dự án", "loai_vb": "Nghị định", "so_hieu": "05/2025/NĐ-CP",
        "trich_yeu": "Sửa đổi, bổ sung một số điều của Nghị định số 08/2022/NĐ-CP ngày 10 tháng 01 năm 2022 của Chính phủ quy định chi tiết một số điều của Luật Bảo vệ môi trường", "co_quan": "Chính phủ",
        "ngay_bh": "06/01/2025", "ngay_hl": "06/01/2025", "trang_thai": "Đang có hiệu lực",
        "thay_the": "Sửa đổi, bổ sung Nghị định số 08/2022/NĐ-CP; được sửa đổi bởi Nghị định 48/2026/NĐ-CP", "chuyen_tiep": "Quy định phân quyền và cắt giảm thủ tục cấp Giấy phép môi trường, Đăng ký môi trường",
        "tags": "MOI_TRUONG, TV-01, TV-02, TV-03, TV-04, XD-01", "link_iv": ""
    },
    {
        "linh_vuc": "Xây dựng & Quản lý dự án", "loai_vb": "Nghị định", "so_hieu": "48/2026/NĐ-CP",
        "trich_yeu": "Sửa đổi, bổ sung một số điều của Nghị định số 08/2022/NĐ-CP ngày 10 tháng 01 năm 2022 của Chính phủ quy định chi tiết một số điều của Luật Bảo vệ môi trường được sửa đổi, bổ sung bởi Nghị định số 05/2025/NĐ-CP ngày 06 tháng 01 năm 2025", "co_quan": "Chính phủ",
        "ngay_bh": "15/05/2026", "ngay_hl": "01/07/2026", "trang_thai": "Đang có hiệu lực",
        "thay_the": "Sửa đổi, bổ sung Nghị định số 08/2022/NĐ-CP và Nghị định số 05/2025/NĐ-CP", "chuyen_tiep": "Đơn giản hóa tối đa thủ tục môi trường cho các công trình xây dựng và dự án đầu tư công hiện hành",
        "tags": "MOI_TRUONG, TV-01, TV-02, TV-03, TV-04, XD-01", "link_iv": ""
    }
]

def load_master_seeds(excel_path: str = EXCEL_PATH, reset: bool = True) -> int:
    """Nạp toàn bộ hạt giống pháp lý Master Seed vào file Excel chuẩn 14 cột với giao diện chuẩn."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Can_Cu_Phap_Ly"
    ws.append(HEADERS_14)

    for idx, item in enumerate(MASTER_SEED_RECORDS, start=1):
        row_data = [
            idx,
            item["linh_vuc"],
            item["loai_vb"],
            item["so_hieu"],
            item["trich_yeu"],
            item["co_quan"],
            item["ngay_bh"],
            item["ngay_hl"],
            item["trang_thai"],
            item["thay_the"],
            item["chuyen_tiep"],
            item["tags"],
            item.get("link_iv", ""),
            now_str
        ]
        ws.append(row_data)

    apply_table_formatting(ws)

    saved_path = excel_path
    try:
        wb.save(excel_path)
    except PermissionError:
        pending_path = excel_path.replace(".xlsx", "_pending.xlsx")
        wb.save(pending_path)
        saved_path = pending_path
        print(f"[!] CẢNH BÁO: Excel đang mở. Đã lưu tạm an toàn vào: {os.path.basename(pending_path)}")

    wb.close()

    try:
        from modules.web_card_generator import generate_mobile_card_web
        generate_mobile_card_web(excel_path=saved_path)
    except Exception as e:
        print(f"[!] Không thể cập nhật Web Card View: {e}")

    total_records = len(MASTER_SEED_RECORDS)
    print(f"✅ ĐÃ TỔNG HỢP TOÀN BỘ SỔ CÁI EXCEL MỚI: {total_records} văn bản chuẩn 14 cột!")
    return total_records


if __name__ == "__main__":
    total = load_master_seeds()
    print(f"🏛️ Tổng số văn bản trong Sổ cái Master: {total}")
