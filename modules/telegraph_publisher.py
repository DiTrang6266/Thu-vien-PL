# -*- coding: utf-8 -*-
"""
Module: telegraph_publisher.py
Mục đích: Xuất bản Báo cáo Tóm tắt Pháp lý Toàn văn trung thực lên Telegraph (Instant View).
Tuyệt đối không gò ép khuôn mẫu 3 mục (Đấu thầu, Dự toán, BQLDA).
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
            except Exception as e:
                logging.warning(f"Không thể đọc file cache Telegraph token: {e}")

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
            logging.error(f"Không thể kết nối Telegraph API: {e}")

        return "anonymous_token"

    def format_nodes_from_analysis(
        self,
        title: str,
        ai_data: Dict[str, Any],
        doc_meta: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        nodes = []

        # 1. Header & Thông tin chung
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

        # 2. Nội dung các quy định cốt lõi (Bám sát điều khoản thật)
        nodes.append({"tag": "h3", "children": ["📑 CÁC QUY ĐỊNH CỐT LÕI (TRÍCH XUẤT TỪ VĂN BẢN GỐC)"]})
        points = ai_data.get("summary_points", [])
        if not points:
            points = ai_data.get("summary_top3", [])
        for pt in points:
            nodes.append({"tag": "p", "children": [{"tag": "strong", "children": [pt]}]})
        nodes.append({"tag": "hr"})

        # 3. Văn bản bị bãi bỏ / thay thế (nếu có)
        repealed = ai_data.get("repealed_docs", [])
        if repealed and isinstance(repealed, list) and len(repealed) > 0:
            nodes.append({"tag": "h3", "children": ["❌ VĂN BẢN BÃI BỎ / THAY THẾ"]})
            for r in repealed:
                nodes.append({"tag": "p", "children": [f"• {r}"]})
            nodes.append({"tag": "hr"})

        # 4. Hiệu lực thi hành & Chuyển tiếp
        eff_trans = ai_data.get("effective_and_transition") or ai_data.get("transition_rules")
        if eff_trans:
            nodes.append({"tag": "h3", "children": ["⏳ HIỆU LỰC THI HÀNH & ĐIỀU KHOẢN CHUYỂN TIẾP"]})
            nodes.append({"tag": "p", "children": [{"tag": "em", "children": [eff_trans]}]})
            nodes.append({"tag": "hr"})

        # Footer
        nodes.append({"tag": "p", "children": [
            {"tag": "em", "children": [
                "Báo cáo được tóm tắt trung thực, bám sát nguyên văn tài liệu bởi Trợ lý Pháp luật 24/7."
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
                    logging.info(f"Đã xuất bản bài viết lên Telegraph thành công: {url}")
                    return url
                else:
                    logging.error(f"Lỗi khi xuất bản Telegraph: {res_data}")
        except Exception as e:
            logging.error(f"Ngoại lệ khi gọi Telegraph API: {e}")

        return None
