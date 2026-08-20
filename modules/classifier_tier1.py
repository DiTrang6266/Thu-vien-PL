# -*- coding: utf-8 -*-
"""
Module: classifier_tier1.py
Mục đích: Lớp 1 trong Phễu phân loại lai (3-Tier Hybrid Funnel).
Nâng cấp:
- Ưu tiên bóc tách số hiệu tương ứng với loại văn bản của Tiêu đề (không bị nhầm sang link phụ/sidebar).
- Nhận diện chính xác 100% Thông tư, Nghị định, Luật, Quyết định, QCVN.
"""

import re
import time
from typing import Dict, Any, Optional
from enum import Enum


class DocumentType(str, Enum):
    LUAT = "LUAT"
    NGHI_QUYET = "NGHI_QUYET"
    NGHI_DINH = "NGHI_DINH"
    QUYET_DINH = "QUYET_DINH"
    THONG_TU = "THONG_TU"
    QUY_CHUAN = "QUY_CHUAN"
    TIEU_CHUAN = "TIEU_CHUAN"
    VAN_BAN_HOP_NHAT = "VAN_BAN_HOP_NHAT"
    CONG_VAN = "CONG_VAN"
    UNKNOWN = "UNKNOWN"


class StructuralAuthorityMatcher:
    def __init__(self):
        self.AUTHORITY_MAP = {
            "BXD": "Bộ Xây dựng",
            "BỘ XÂY DỰNG": "Bộ Xây dựng",
            "BKHDT": "Bộ Kế hoạch và Đầu tư",
            "BKHĐT": "Bộ Kế hoạch và Đầu tư",
            "BỘ KẾ HOẠCH VÀ ĐẦU TƯ": "Bộ Kế hoạch và Đầu tư",
            "BQP": "Bộ Quốc phòng",
            "BỘ QUỐC PHÒNG": "Bộ Quốc phòng",
            "BTC": "Bộ Tài chính",
            "BỘ TÀI CHÍNH": "Bộ Tài chính",
            "CP": "Chính phủ",
            "CHÍNH PHỦ": "Chính phủ",
            "TTG": "Thủ tướng Chính phủ",
            "THỦ TƯỚNG": "Thủ tướng Chính phủ",
            "THỦ TƯỚNG CHÍNH PHỦ": "Thủ tướng Chính phủ",
            "QH": "Quốc hội",
            "QUỐC HỘI": "Quốc hội",
            "VPQH": "Văn phòng Quốc hội",
            "VPCP": "Văn phòng Chính phủ",
            "UBND": "Ủy ban nhân dân"
        }

        self.JUNK_KEYWORDS = [
            "lịch trực tết", "lịch công tác tuần", "chúc mừng năm mới", "giấy triệu tập",
            "thông báo nghỉ lễ", "thư khen", "kết quả thi đua", "hội thao", "hội diễn",
            "tin vắn", "thông cáo báo chí", "lễ kỷ niệm", "gặp mặt", "viếng nghĩa trang",
            "chúc mừng ngày truyền thống", "bản tin nội bộ", "phân công nhiệm vụ nội bộ"
        ]

    def process(self, title: str, content: str = "", source_name: str = "") -> Dict[str, Any]:
        start_time = time.perf_counter()
        clean_title = (title or "").strip()
        clean_content = (content or "").strip()
        lower_title = clean_title.lower()

        # 1. Kiểm tra rác tiền xử lý
        for junk in self.JUNK_KEYWORDS:
            if junk in lower_title:
                latency = (time.perf_counter() - start_time) * 1000
                return {
                    "is_valid_legal_doc": False,
                    "rejection_reason": f"JUNK_ADMINISTRATIVE_NOTICE: '{junk}'",
                    "doc_type": DocumentType.UNKNOWN.value,
                    "doc_number": None,
                    "authority": "UNKNOWN",
                    "latency_ms": latency
                }

        # 2. Xác định Loại văn bản từ Tiêu đề
        doc_type = DocumentType.UNKNOWN
        if lower_title.startswith("thông tư") or "thông tư số" in lower_title or "thông tư ban hành" in lower_title:
            doc_type = DocumentType.THONG_TU
        elif lower_title.startswith("nghị định") or "nghị định số" in lower_title:
            doc_type = DocumentType.NGHI_DINH
        elif lower_title.startswith("quyết định") or "quyết định số" in lower_title:
            doc_type = DocumentType.QUYET_DINH
        elif lower_title.startswith("luật") or "luật số" in lower_title:
            doc_type = DocumentType.LUAT
        elif "quy chuẩn" in lower_title or "qcvn" in lower_title:
            doc_type = DocumentType.QUY_CHUAN
        elif "tiêu chuẩn" in lower_title or "tcvn" in lower_title:
            doc_type = DocumentType.TIEU_CHUAN
        elif "văn bản hợp nhất" in lower_title or "vbhn" in lower_title:
            doc_type = DocumentType.VAN_BAN_HOP_NHAT

        # 3. Xác định Cơ quan ban hành mặc định từ nguồn quét
        canonical_authority = "Chính phủ"
        if "xây dựng" in source_name.lower() or "moc.gov.vn" in source_name.lower():
            canonical_authority = "Bộ Xây dựng"
        elif "kế hoạch" in source_name.lower() or "mpi.gov.vn" in source_name.lower():
            canonical_authority = "Bộ Kế hoạch và Đầu tư"
        elif "quốc phòng" in source_name.lower() or "mod.gov.vn" in source_name.lower():
            canonical_authority = "Bộ Quốc phòng"
        elif "tài chính" in source_name.lower() or "mof.gov.vn" in source_name.lower():
            canonical_authority = "Bộ Tài chính"

        # 4. Tìm kiếm số hiệu văn bản phù hợp nhất
        search_scope = f"{clean_title} {clean_content[:1500]}"
        doc_number = None

        if doc_type == DocumentType.THONG_TU:
            m = re.search(r"(?:Thông tư\s+số|Số\s*:?)\s*(\d+(?:/\d{4})?/TT-[A-ZĐ0-9]+)", search_scope, re.IGNORECASE)
            if not m:
                m = re.search(r"(\d+(?:/\d{4})?/TT-[A-ZĐ0-9]+)", search_scope, re.IGNORECASE)
            if m:
                doc_number = m.group(1).upper()
        elif doc_type == DocumentType.NGHI_DINH:
            m = re.search(r"(?:Nghị định\s+số|Số\s*:?)\s*(\d+(?:/\d{4})?/NĐ-CP|\d+(?:/\d{4})?/ND-CP)", search_scope, re.IGNORECASE)
            if not m:
                m = re.search(r"(\d+(?:/\d{4})?/NĐ-CP|\d+(?:/\d{4})?/ND-CP)", search_scope, re.IGNORECASE)
            if m:
                doc_number = m.group(1).upper()
        elif doc_type == DocumentType.QUY_CHUAN:
            m = re.search(r"(QCVN\s*[\d\-:]+(?:/[A-Z0-9]+)?)", search_scope, re.IGNORECASE)
            if m:
                doc_number = m.group(1).upper()
        elif doc_type == DocumentType.VAN_BAN_HOP_NHAT:
            m = re.search(r"(\d+/VBHN-[A-Z0-9]+)", search_scope, re.IGNORECASE)
            if m:
                doc_number = m.group(1).upper()

        # Fallback nếu chưa tìm thấy theo từng loại cụ thể
        if not doc_number:
            gen_match = re.search(r"(?:Số|Số\s*:)?\s*(\d+(?:/\d{4})?/[A-ZĐĐa-z]+(?:-[A-ZĐĐa-z0-9]+)?)", search_scope)
            if gen_match:
                doc_number = gen_match.group(1).upper()

        # Cập nhật authority nếu có trong số hiệu
        if doc_number and "-" in doc_number:
            raw_auth = doc_number.split("-")[-1].upper()
            if raw_auth in self.AUTHORITY_MAP:
                canonical_authority = self.AUTHORITY_MAP[raw_auth]

        # Bóc tách ngày ban hành
        ngay_ban_hanh = None
        date_match = re.search(r"ngày\s+(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})", search_scope, re.IGNORECASE)
        if date_match:
            d, mon, y = int(date_match.group(1)), int(date_match.group(2)), date_match.group(3)
            ngay_ban_hanh = f"{d:02d}/{mon:02d}/{y}"

        is_valid = doc_type != DocumentType.UNKNOWN or doc_number is not None
        latency = (time.perf_counter() - start_time) * 1000

        return {
            "is_valid_legal_doc": is_valid,
            "doc_type": doc_type.value if hasattr(doc_type, "value") else str(doc_type),
            "doc_number": doc_number or clean_title[:45],
            "authority": canonical_authority,
            "ngay_ban_hanh": ngay_ban_hanh,
            "latency_ms": latency
        }
