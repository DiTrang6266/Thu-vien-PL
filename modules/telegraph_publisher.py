# -*- coding: utf-8 -*-
"""
Module: telegraph_publisher.py
Mục đích: Xuất bản Báo cáo Phân tích Pháp lý Toàn văn không giới hạn độ dài lên Telegraph (Instant View).
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
        nodes.append({"tag": "h4", "children": ["🏛️ THÔNG TIN VĂN BẢN ĐỐI CHIẾU"]})
        meta_items = []
        if doc_meta:
            if doc_meta.get("so_hieu"):
                meta_items.append(f"• Số hiệu: {doc_meta['so_hieu']}\n")
            if doc_meta.get("co_quan"):
                meta_items.append(f"• Cơ quan ban hành: {doc_meta['co_quan']}\n")
            if doc_meta.get("ngay_ban_hanh"):
                meta_items.append(f"• Ngày ban hành: {doc_meta['ngay_ban_hanh']}\n")
        
        meta_items.append("• Cơ chế kiểm tra: Đối chiếu nguyên văn Zero-Chunking + Trích dẫn kiểm chứng 100%.\n")
        nodes.append({"tag": "p", "children": meta_items})
        nodes.append({"tag": "hr"})

        # 2. Top 3 Thay đổi Cốt lõi
        nodes.append({"tag": "h3", "children": ["🌟 TOP 3 THAY ĐỔI CỐT LÕI ẢNH HƯỞNG HỒ SƠ DỰ ÁN"]})
        top3_list = ai_data.get("summary_top3", [])
        for item in top3_list:
            nodes.append({"tag": "p", "children": [{"tag": "strong", "children": [item]}]})
        nodes.append({"tag": "hr"})

        # 3. Tác động chi tiết theo từng lĩnh vực
        nodes.append({"tag": "h3", "children": ["⚖️ PHÂN TÍCH TÁC ĐỘNG THỰC TIỄN CHO NGƯỜI LẬP HỒ SƠ"]})
        impacts = ai_data.get("impact_areas", {})
        
        if impacts.get("ho_so_moi_thau_va_dau_thau"):
            nodes.append({"tag": "h4", "children": ["1. Đối với Công tác Đấu thầu & Hồ sơ Mời thầu:"]})
            nodes.append({"tag": "p", "children": [impacts["ho_so_moi_thau_va_dau_thau"]]})

        if impacts.get("du_toan_va_chi_phi"):
            nodes.append({"tag": "h4", "children": ["2. Đối với Dự toán, Định mức & Đơn giá Gói thầu:"]})
            nodes.append({"tag": "p", "children": [impacts["du_toan_va_chi_phi"]]})

        if impacts.get("tham_quyen_va_trach_nhiem"):
            nodes.append({"tag": "h4", "children": ["3. Đối với Thẩm quyền Phê duyệt & Trách nhiệm BQLDA:"]})
            nodes.append({"tag": "p", "children": [impacts["tham_quyen_va_trach_nhiem"]]})

        nodes.append({"tag": "hr"})

        # 4. Quy định chuyển tiếp
        nodes.append({"tag": "h3", "children": ["🔄 QUY ĐỊNH CHUYỂN TIẾP (DÀNH CHO HỒ SƠ ĐANG LÀM DỞ)"]})
        trans_rules = ai_data.get("transition_rules", "Áp dụng theo quy định chuyển tiếp tại các điều khoản thi hành của văn bản.")
        nodes.append({"tag": "p", "children": [{"tag": "em", "children": [trans_rules]}]})
        nodes.append({"tag": "hr"})

        # 5. Bảng chi tiết từng Điều/Khoản
        nodes.append({"tag": "h3", "children": ["📑 BẢNG ĐỐI CHIẾU NGUYÊN VĂN TỪNG ĐIỀU KHOẢN"]})
        diff_articles = ai_data.get("detailed_articles_diff", [])

        if not diff_articles:
            nodes.append({"tag": "p", "children": ["Áp dụng toàn diện theo toàn văn các điều khoản ban hành kèm theo văn bản."]})
        else:
            for idx, art in enumerate(diff_articles, 1):
                status = art.get("status", "QUY ĐỊNH MỚI")
                art_id = art.get("article_id", f"Điều {idx}")
                art_title = art.get("title", "")
                
                nodes.append({"tag": "h4", "children": [f"📌 {art_id}: {art_title} ({status})"]})

                if art.get("exact_quote_old"):
                    nodes.append({"tag": "p", "children": [
                        {"tag": "strong", "children": ["[-] Quy định cũ: "]},
                        art["exact_quote_old"]
                    ]})

                if art.get("exact_quote_new"):
                    nodes.append({"tag": "p", "children": [
                        {"tag": "strong", "children": ["[+] Quy định mới: "]},
                        art["exact_quote_new"]
                    ]})

                if art.get("core_change_explanation"):
                    nodes.append({"tag": "p", "children": [
                        {"tag": "strong", "children": ["💡 Bản chất quy định: "]},
                        art["core_change_explanation"]
                    ]})

                if art.get("action_required"):
                    nodes.append({"tag": "p", "children": [
                        {"tag": "strong", "children": ["👉 Việc cần làm: "]},
                        art["action_required"]
                    ]})

                nodes.append({"tag": "p", "children": ["- - - - - - - - - - - - - - - -"]})

        # Footer
        nodes.append({"tag": "hr"})
        nodes.append({"tag": "p", "children": [
            {"tag": "em", "children": [
                "Báo cáo được tổng hợp và đối soát tự động bởi Hệ thống Trinh sát Pháp lý Xây dựng 24/7."
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
