# -*- coding: utf-8 -*-
"""
Module: legal_diff.py
Mục đích: Đối chiếu cấu trúc và từng từ ngữ giữa Văn bản gốc và Văn bản sửa đổi bổ sung.
Tạo chuỗi Redline Track Changes, bảng so sánh đa cột và lớp kiểm tra trích dẫn gốc 100%.
"""

import difflib
import re
from typing import Dict, List, Any, Optional, Tuple


class LegalDocumentDiffer:
    """
    Công cụ đối chiếu văn bản pháp lý chuyên sâu.
    """

    def __init__(self):
        pass

    def diff_words(self, old_text: str, new_text: str) -> Dict[str, Any]:
        """
        So sánh ở cấp độ từng từ ngữ giữa văn bản cũ và mới.
        Sinh ra chuỗi HTML/Markdown có đánh dấu gạch ngang (cũ) và tô sáng (mới).
        """
        old_words = re.findall(r'\S+|\s+', old_text)
        new_words = re.findall(r'\S+|\s+', new_text)

        matcher = difflib.SequenceMatcher(None, old_words, new_words)
        html_diff = []
        md_diff = []
        
        has_changes = False
        words_added = 0
        words_removed = 0

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                segment = "".join(old_words[i1:i2])
                html_diff.append(segment)
                md_diff.append(segment)
            elif tag == 'delete':
                has_changes = True
                segment = "".join(old_words[i1:i2])
                words_removed += len(old_words[i1:i2])
                html_diff.append(f'<del style="color:#d93025; background-color:#fce8e6; text-decoration:line-through;">{segment}</del>')
                md_diff.append(f"~~{segment}~~")
            elif tag == 'insert':
                has_changes = True
                segment = "".join(new_words[j1:j2])
                words_added += len(new_words[j1:j2])
                html_diff.append(f'<ins style="color:#188038; background-color:#e6f4ea; text-decoration:none; font-weight:bold;">{segment}</ins>')
                md_diff.append(f"**{segment}**")
            elif tag == 'replace':
                has_changes = True
                del_seg = "".join(old_words[i1:i2])
                ins_seg = "".join(new_words[j1:j2])
                words_removed += len(old_words[i1:i2])
                words_added += len(new_words[j1:j2])
                html_diff.append(f'<del style="color:#d93025; background-color:#fce8e6; text-decoration:line-through;">{del_seg}</del> <ins style="color:#188038; background-color:#e6f4ea; text-decoration:none; font-weight:bold;">{ins_seg}</ins>')
                md_diff.append(f"~~{del_seg}~~ **{ins_seg}**")

        return {
            "has_changes": has_changes,
            "words_added": words_added,
            "words_removed": words_removed,
            "html_redline": "".join(html_diff),
            "md_redline": "".join(md_diff)
        }

    def compare_articles(self, old_articles: Dict[str, Any], new_articles: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        So sánh danh sách các Điều giữa 2 văn bản.
        Phân loại: SỬA ĐỔI, BỔ SUNG, BÃI BỎ, GIỮ NGUYÊN.
        """
        comparison_results = []
        all_article_keys = list(dict.fromkeys(list(old_articles.keys()) + list(new_articles.keys())))

        for art_key in all_article_keys:
            old_art = old_articles.get(art_key)
            new_art = new_articles.get(art_key)

            if old_art and not new_art:
                # Bị bãi bỏ trong văn bản mới
                comparison_results.append({
                    "article_id": art_key,
                    "title": old_art.get("title", ""),
                    "status": "BÃI BỎ",
                    "old_text": old_art.get("full_text", ""),
                    "new_text": "",
                    "old_page": old_art.get("page_start", 1),
                    "new_page": None,
                    "redline_html": f'<del style="color:#d93025; background-color:#fce8e6; text-decoration:line-through;">{old_art.get("full_text", "")}</del>',
                    "redline_md": f"~~{old_art.get('full_text', '')}~~",
                    "summary_impact": f"Điều luật này đã bị bãi bỏ hoàn toàn."
                })
            elif new_art and not old_art:
                # Điều mới được bổ sung
                comparison_results.append({
                    "article_id": art_key,
                    "title": new_art.get("title", ""),
                    "status": "BỔ SUNG MỚI",
                    "old_text": "",
                    "new_text": new_art.get("full_text", ""),
                    "old_page": None,
                    "new_page": new_art.get("page_start", 1),
                    "redline_html": f'<ins style="color:#188038; background-color:#e6f4ea; font-weight:bold;">{new_art.get("full_text", "")}</ins>',
                    "redline_md": f"**{new_art.get('full_text', '')}**",
                    "summary_impact": f"Quy định mới được bổ sung hoàn toàn."
                })
            else:
                # Có ở cả 2 bản -> So sánh nội dung
                diff_res = self.diff_words(old_art.get("full_text", ""), new_art.get("full_text", ""))
                if diff_res["has_changes"]:
                    comparison_results.append({
                        "article_id": art_key,
                        "title": new_art.get("title", old_art.get("title", "")),
                        "status": "SỬA ĐỔI / THAY THẾ",
                        "old_text": old_art.get("full_text", ""),
                        "new_text": new_art.get("full_text", ""),
                        "old_page": old_art.get("page_start", 1),
                        "new_page": new_art.get("page_start", 1),
                        "redline_html": diff_res["html_redline"],
                        "redline_md": diff_res["md_redline"],
                        "words_added": diff_res["words_added"],
                        "words_removed": diff_res["words_removed"],
                        "summary_impact": f"Có thay đổi câu chữ, thông số hoặc quy trình."
                    })
                else:
                    # Giữ nguyên
                    pass

        return comparison_results

    @staticmethod
    def verify_exact_quote(quote: str, source_text: str) -> bool:
        """
        Lớp Hậu kiểm Chống Ảo giác:
        Kiểm tra xem chuỗi trích dẫn mà AI đưa ra có nằm trong văn bản gốc 100% không.
        """
        if not quote or not source_text:
            return False
        
        # Chuẩn hóa khoảng trắng để tránh lỗi do xuống dòng
        norm_quote = " ".join(quote.strip().split()).lower()
        norm_source = " ".join(source_text.strip().split()).lower()

        return norm_quote in norm_source
