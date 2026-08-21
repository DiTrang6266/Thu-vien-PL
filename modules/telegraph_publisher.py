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

        # Bỏ khối THÔNG TIN VĂN BẢN trùng lặp vì đã hiển thị trên tin nhắn Telegram.
        # Đi thẳng vào TOP thay đổi cốt lõi tác động đến dự án.

        # 2. Đánh giá Tác động Nghiệp vụ Tổng quan
        impact = ai_data.get("impact_summary")
        summary_top3 = ai_data.get("summary_top3")
        if summary_top3 and isinstance(summary_top3, list):
            nodes.append({"tag": "h3", "children": ["⚡ TOP 3 THAY ĐỔI CỐT LÕI TÁC ĐỘNG ĐẾN DỰ ÁN"]})
            top_items = []
            for item in summary_top3:
                top_items.append(f"• {item}\n")
            nodes.append({"tag": "p", "children": top_items})
            nodes.append({"tag": "hr"})
        elif impact:
            nodes.append({"tag": "h3", "children": ["⚡ TÁC ĐỘNG TRỰC TIẾP ĐẾN DỰ ÁN & HỒ SƠ"]})
            nodes.append({"tag": "p", "children": [{"tag": "strong", "children": [impact]}]})
            nodes.append({"tag": "hr"})

        # 3. Phân tích chi tiết theo từng mảng nghiệp vụ (impact_areas)
        impact_areas = ai_data.get("impact_areas")
        if impact_areas and isinstance(impact_areas, dict):
            nodes.append({"tag": "h3", "children": ["📂 TÁC ĐỘNG THEO MẢNG NGHIỆP VỤ"]})
            area_nodes = []
            for area_k, area_v in impact_areas.items():
                area_label = area_k.replace("_", " ").title()
                if "moi_thau" in area_k or "dau_thau" in area_k:
                    area_label = "📋 Hồ sơ mời thầu & Đấu thầu"
                elif "du_toan" in area_k or "chi_phi" in area_k:
                    area_label = "💰 Dự toán & Quản lý chi phí"
                elif "tham_quyen" in area_k or "trach_nhiem" in area_k:
                    area_label = "⚖️ Thẩm quyền & Trách nhiệm"
                area_nodes.append({"tag": "strong", "children": [f"• {area_label}:\n"]})
                area_nodes.append(f"  {area_v}\n\n")
            nodes.append({"tag": "p", "children": area_nodes})
            nodes.append({"tag": "hr"})

        # 4. Các Quy định Cốt lõi & Hành động Bắt buộc
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

        # 5. Bảng Đối chiếu Cũ vs Mới (detailed_articles_diff / comparative_table)
        diff_data = ai_data.get("detailed_articles_diff") or ai_data.get("comparative_table") or []
        if diff_data and isinstance(diff_data, list) and len(diff_data) > 0:
            nodes.append({"tag": "h3", "children": ["🔄 BẢNG ĐỐI CHIẾU ĐIỂM MỚI (CŨ VS MỚI)"]})
            for row in diff_data:
                if isinstance(row, dict):
                    art_id = row.get("article_id") or row.get("item", "")
                    art_title = row.get("title", "")
                    status = row.get("status", "")
                    old_r = row.get("exact_quote_old") or row.get("old_rule", "")
                    new_r = row.get("exact_quote_new") or row.get("new_rule", "")
                    diff = row.get("core_change_explanation") or row.get("key_difference", "")
                    action = row.get("action_required", "")

                    children = [{"tag": "strong", "children": [f"📌 {art_id} - {art_title} [{status}]:\n"]}]
                    if old_r:
                        children.append(f"• Cũ: {old_r}\n")
                    if new_r:
                        children.append(f"• Mới: {new_r}\n")
                    if diff:
                        children.append({"tag": "em", "children": [f"➔ Thay đổi: {diff}\n"]})
                    if action:
                        children.append({"tag": "strong", "children": [f"👉 Hành động: {action}\n"]})
                    nodes.append({"tag": "p", "children": children})
            nodes.append({"tag": "hr"})

        # 6. Cảnh báo rủi ro & Bẫy pháp lý
        risks = ai_data.get("compliance_risks")
        if risks:
            nodes.append({"tag": "h3", "children": ["⚠️ CẢNH BÁO RỦI RO & ĐIỂM LƯU Ý KHI THANH KIỂM TRA"]})
            nodes.append({"tag": "p", "children": [risks]})
            nodes.append({"tag": "hr"})

        # 7. Văn bản bị bãi bỏ / thay thế
        repealed = ai_data.get("repealed_docs", [])
        if repealed and isinstance(repealed, list) and len(repealed) > 0:
            nodes.append({"tag": "h3", "children": ["❌ VĂN BẢN BÃI BỎ / THAY THẾ"]})
            for r in repealed:
                nodes.append({"tag": "p", "children": [f"• {r}"]})
            nodes.append({"tag": "hr"})

        # 8. Hiệu lực thi hành & Chuyển tiếp (transition_rules / effective_and_transition)
        eff_trans = ai_data.get("transition_rules") or ai_data.get("effective_and_transition")
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
        analysis_data: Optional[Dict[str, Any]] = None,
        doc_item: Optional[Dict[str, Any]] = None,
        ai_data: Optional[Dict[str, Any]] = None,
        doc_meta: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        try:
            effective_ai_data = analysis_data if analysis_data is not None else ai_data or {}
            effective_doc_meta = doc_item if doc_item is not None else doc_meta
            nodes = self.format_nodes_from_analysis(title, effective_ai_data, effective_doc_meta)
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
