# -*- coding: utf-8 -*-
"""
Module: telegraph_publisher.py
Mục đích: Xuất bản Báo cáo Tham mưu Nghiệp vụ Thực chiến lên Telegraph (Instant View).
Hiển thị:
1. Thông tin văn bản & Phạm vi nghiệp vụ.
2. Tóm tắt tác động trực tiếp đến Ban QLDA, Dự toán, Đấu thầu.
3. Các quy định cốt lõi & Hành động bắt buộc.
4. Bảng đối chiếu Cũ vs Mới (Redline Table).
5. Cảnh báo rủi ro pháp lý & Bẫy thanh kiểm tra.
6. Thẻ căn cứ pháp lý Nghị định 30.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class TelegraphPublisher:
    API_BASE = "https://api.telegra.ph"

    def __init__(self, token_cache_path: Optional[str] = None):
        self.token_cache_path = token_cache_path or os.path.join(
            os.path.dirname(__file__), "..", "data", "telegraph_token.json"
        )
        self.access_token = self._load_or_create_account()

    def _load_or_create_account(self) -> str:
        os.makedirs(os.path.dirname(self.token_cache_path), exist_ok=True)
        if os.path.exists(self.token_cache_path):
            try:
                with open(self.token_cache_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    token = data.get("access_token")
                    if token:
                        return token
            except Exception:
                pass

        try:
            with httpx.Client(timeout=15.0, verify=False) as client:
                res = client.post(
                    f"{self.API_BASE}/createAccount",
                    json={
                        "short_name": "TrolyPL",
                        "author_name": "Trợ lý Pháp Luật Xây Dựng",
                        "author_url": "https://t.me/Troly_PL_bot"
                    }
                )
                res_data = res.json()
                if res_data.get("ok"):
                    token = res_data["result"]["access_token"]
                    with open(self.token_cache_path, "w", encoding="utf-8") as f:
                        json.dump({"access_token": token}, f, ensure_ascii=False, indent=2)
                    return token
        except Exception as e:
            logging.error(f"Lỗi Telegraph account: {e}")

        return "anonymous_token"

    def format_nodes_from_analysis(
        self,
        title: str,
        ai_data: Dict[str, Any],
        doc_meta: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        nodes = []

        # 1. Header & Thông số hành chính
        nodes.append({"tag": "h4", "children": ["🏛️ THÔNG TIN VĂN BẢN"]})
        meta_items = []
        if doc_meta:
            if doc_meta.get("so_hieu"):
                meta_items.append(f"• Số hiệu: {doc_meta['so_hieu']}\n")
            if doc_meta.get("co_quan"):
                meta_items.append(f"• Cơ quan ban hành: {doc_meta['co_quan']}\n")
            if doc_meta.get("ngay_ban_hanh"):
                meta_items.append(f"• Ngày ban hành: {doc_meta['ngay_ban_hanh']}\n")
        
        meta_items.append("• Phạm vi: Áp dụng phổ quát toàn quốc.\n")
        nodes.append({"tag": "p", "children": meta_items})
        nodes.append({"tag": "hr"})

        # 2. Đánh giá Tác động Nghiệp vụ Tổng quan
        impact = ai_data.get("impact_summary")
        if impact:
            nodes.append({"tag": "h3", "children": ["⚡ TÁC ĐỘNG TRỰC TIẾP ĐẾN DỰ ÁN & HỒ SƠ"]})
            nodes.append({"tag": "p", "children": [{"tag": "strong", "children": [impact]}]})
            nodes.append({"tag": "hr"})

        # 3. Các Quy định Cốt lõi & Hành động Bắt buộc
        points = ai_data.get("substantive_points", [])
        if points and isinstance(points, list):
            nodes.append({"tag": "h3", "children": ["📋 CÁC QUY ĐỊNH KỸ THUẬT & NGHIỆP VỤ CỐT LÕI"]})
            for pt in points:
                if isinstance(pt, dict):
                    clause = pt.get("clause", "")
                    p_title = pt.get("title", "")
                    content = pt.get("content", "")
                    action = pt.get("action_required", "")

                    item_children = [
                        {"tag": "strong", "children": [f"{clause} - {p_title}\n"]},
                        f"• Nội dung: {content}\n"
                    ]
                    if action:
                        item_children.append({"tag": "em", "children": [f"👉 Hành động bắt buộc: {action}\n"]})
                    
                    nodes.append({"tag": "p", "children": item_children})
                elif isinstance(pt, str):
                    nodes.append({"tag": "p", "children": [pt]})
            nodes.append({"tag": "hr"})

        # 4. Bảng Đối chiếu Cũ vs Mới (nếu có)
        table_data = ai_data.get("comparative_table", [])
        if table_data and isinstance(table_data, list) and len(table_data) > 0:
            nodes.append({"tag": "h3", "children": ["🔄 BẢNG ĐỐI CHIẾU ĐIỂM MỚI (CŨ VS MỚI)"]})
            for row in table_data:
                if isinstance(row, dict):
                    item_name = row.get("item", "")
                    old_r = row.get("old_rule", "")
                    new_r = row.get("new_rule", "")
                    diff = row.get("key_difference", "")
                    nodes.append({"tag": "p", "children": [
                        {"tag": "strong", "children": [f"📌 {item_name}:\n"]},
                        f"• Quy định cũ: {old_r}\n",
                        f"• Quy định mới: {new_r}\n",
                        {"tag": "em", "children": [f"➔ Thay đổi cốt lõi: {diff}\n"]}
                    ]})
            nodes.append({"tag": "hr"})

        # 5. Cảnh báo rủi ro & Bẫy pháp lý
        risks = ai_data.get("compliance_risks")
        if risks:
            nodes.append({"tag": "h3", "children": ["⚠️ CẢNH BÁO RỦI RO & ĐIỂM LƯU Ý KHI THANH KIỂM TRA"]})
            nodes.append({"tag": "p", "children": [risks]})
            nodes.append({"tag": "hr"})

        # 6. Văn bản bị bãi bỏ / thay thế
        repealed = ai_data.get("repealed_docs", [])
        if repealed and isinstance(repealed, list) and len(repealed) > 0:
            nodes.append({"tag": "h3", "children": ["❌ VĂN BẢN BÃI BỎ / THAY THẾ"]})
            for r in repealed:
                nodes.append({"tag": "p", "children": [f"• {r}"]})
            nodes.append({"tag": "hr"})

        # 7. Hiệu lực thi hành & Chuyển tiếp
        eff_trans = ai_data.get("effective_and_transition")
        if eff_trans:
            nodes.append({"tag": "h3", "children": ["⏳ HIỆU LỰC THI HÀNH & ĐIỀU KHOẢN CHUYỂN TIẾP"]})
            nodes.append({"tag": "p", "children": [{"tag": "em", "children": [eff_trans]}]})
            nodes.append({"tag": "hr"})

        # Footer
        nodes.append({"tag": "p", "children": [
            {"tag": "em", "children": [
                "Báo cáo Tham mưu Nghiệp vụ Thực chiến được thẩm định và lập tự động bởi Trợ lý Pháp luật 24/7."
            ]}
        ]})

        return nodes

    def publish_report(
        self,
        title: str,
        analysis_data: Dict[str, Any],
        doc_item: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        try:
            nodes = self.format_nodes_from_analysis(title, analysis_data, doc_item)
            payload = {
                "access_token": self.access_token,
                "title": title[:100],
                "author_name": "Trợ lý Pháp Luật Xây Dựng",
                "author_url": "https://t.me/Troly_PL_bot",
                "content": nodes,
                "return_content": False
            }

            with httpx.Client(timeout=20.0, verify=False) as client:
                res = client.post(f"{self.API_BASE}/createPage", json=payload)
                res_data = res.json()
                if res_data.get("ok"):
                    url = res_data["result"]["url"]
                    logging.info(f"Đã xuất bản bài viết lên Telegraph: {url}")
                    return url
                else:
                    logging.error(f"Lỗi xuất bản Telegraph: {res_data}")
        except Exception as e:
            logging.error(f"Ngoại lệ Telegraph: {e}")

        return None
