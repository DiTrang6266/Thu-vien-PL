# -*- coding: utf-8 -*-
"""
Kiểm thử tự động cho module legal_resolver.py.
"""

import pytest
from modules.legal_resolver import resolve_legal_url

def test_resolve_legal_url_basic():
    # Test phân giải Luật Đấu thầu / Xây dựng
    url = resolve_legal_url("24/2024/NĐ-CP")
    assert url.startswith("http")
    assert ("thuvienphapluat.vn" in url or "chinhphu.vn" in url or "vbpl.vn" in url)

def test_resolve_legal_url_fallback():
    # Test fallback khi số hiệu rỗng hoặc MỚI
    url_empty = resolve_legal_url("")
    assert url_empty == "https://thuvienphapluat.vn"

    url_new = resolve_legal_url("MỚI")
    assert url_new == "https://thuvienphapluat.vn"

def test_resolve_legal_url_complex():
    # Test với số hiệu Bộ Quốc Phòng
    url_bqp = resolve_legal_url("101/2026/TT-BQP")
    assert url_bqp.startswith("http")
    assert "101" in url_bqp or "tim-van-ban" in url_bqp
