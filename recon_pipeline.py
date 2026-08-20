# -*- coding: utf-8 -*-
"""
Hệ thống Trinh sát & Đối chiếu Văn bản Pháp luật 24/7 (Zero-Cost Watchdog Engine)
Tích hợp:
- Lớp 1: Bóc tách Thể thức & Thẩm quyền theo Nghị định 30/2020/NĐ-CP (classifier_tier1)
- Lớp 2: Bộ lọc Ngữ nghĩa Chuyên ngành Siêu tốc 3-5ms (classifier_tier2)
- Lớp 3: Bộ não AI Gemini + Pydantic Schema (ai_analyzer)
- Đồng bộ tự động 2 chiều Sổ cái Master Excel (Kho_Can_Cu_Phap_Ly.xlsx)
- Bắn Telegram Thông minh: Cảnh báo khai tử (<s>...</s>) + Thẻ căn cứ 1-chạm (<code>...</code>) + PDF gốc đính kèm.
"""

import os
import sys
import json
import hashlib
import urllib.parse
from datetime import datetime
from typing import List, Dict, Any, Optional

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import httpx
import feedparser
from bs4 import BeautifulSoup

from modules.classifier_tier1 import StructuralAuthorityMatcher
from modules.classifier_tier2 import SemanticDomainFilter
from modules.ai_analyzer import LegalAIAnalyzer
from modules.excel_sync_engine import LegalExcelSyncEngine
from modules.telegraph_publisher import TelegraphPublisher

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DOWNLOADS_DIR = os.path.join(DATA_DIR, "downloads")
KNOWN_DOCS_FILE = os.path.join(DATA_DIR, "known_documents.json")
EXCEL_LEGAL_PATH = os.path.join(BASE_DIR, "Kho_Can_Cu_Phap_Ly.xlsx")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

FEED_SOURCES = [
    {
        "name": "Công báo Nước CHXHCN Việt Nam (Văn bản mới)",
        "url": "https://congbao.chinhphu.vn/cac-van-ban-moi-ban-hanh.rss",
        "weight": 1.0
    },
    {
        "name": "Công báo Nước CHXHCN Việt Nam (Số mới đăng)",
        "url": "http://congbao.chinhphu.vn/cac-so-cong-bao-moi-dang.rss",
        "weight": 1.0
    },
    {
        "name": "Bộ Xây dựng (Văn bản quy phạm pháp luật mới)",
        "url": "https://moc.gov.vn/rss/1196/gioi-thieu-van-ban-moi.rss",
        "weight": 1.0
    },
    {
        "name": "Bộ Xây dựng (Chỉ đạo điều hành chuyên ngành)",
        "url": "https://moc.gov.vn/rss/1176/tin-chi-dao--dieu-hanh.rss",
        "weight": 0.8
    },
    {
        "name": "Bộ Kế hoạch và Đầu tư (Văn bản Đấu thầu & Đầu tư công)",
        "url": "https://www.mpi.gov.vn/Pages/rss.aspx",
        "weight": 1.0
    }
]


def log(msg: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {msg}"
    print(formatted)
    try:
        with open(os.path.join(DATA_DIR, "nhat_ky_trinh_sat.log"), "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception:
        pass


def load_known_documents() -> set:
    if os.path.exists(KNOWN_DOCS_FILE):
        try:
            with open(KNOWN_DOCS_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()


def save_known_documents(known_docs: set):
    try:
        with open(KNOWN_DOCS_FILE, "w", encoding="utf-8") as f:
            json.dump(sorted(list(known_docs)), f, ensure_ascii=False, indent=2)
    except Exception as e:
        log(f"❌ Lỗi lưu known_documents: {e}")


def normalize_url(base_url: str, link: str) -> str:
    if not link:
        return ""
    link = link.strip()
    if link.startswith("http:moc.gov.vn"):
        link = "https://moc.gov.vn" + link[len("http:moc.gov.vn"):]
    if link.startswith("//"):
        return "https:" + link
    if link.startswith("http://") or link.startswith("https://"):
        return link
    return urllib.parse.urljoin(base_url, link)


def extract_direct_pdf_link(article_url: str) -> Optional[str]:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://vanban.chinhphu.vn/"
        }
        with httpx.Client(timeout=15.0, headers=headers, follow_redirects=True, verify=False) as client:
            res = client.get(article_url)
            if res.status_code != 200:
                return None
            soup = BeautifulSoup(res.text, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                if ".pdf" in href.lower() or "download" in href.lower() or "file_name=" in href.lower():
                    return normalize_url(article_url, href)
    except Exception:
        pass
    return None


def download_official_pdf(pdf_url: str, doc_id: str) -> Optional[str]:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Referer": "https://vanban.chinhphu.vn/"
        }
        with httpx.Client(timeout=45.0, headers=headers, follow_redirects=True, verify=False) as client:
            res = client.get(pdf_url)
            if res.status_code == 200 and len(res.content) > 1000:
                clean_name = f"{doc_id[:16]}_van_ban_goc.pdf"
                local_path = os.path.join(DOWNLOADS_DIR, clean_name)
                with open(local_path, "wb") as f:
                    f.write(res.content)
                log(f"💾 Đã tải và lưu trữ file PDF thành công ({len(res.content)} bytes): {local_path}")
                return local_path
    except Exception as e:
        log(f"⚠️ Lỗi tải file PDF: {e}")
    return None


def send_telegram_alert(
    item: Dict[str, Any],
    tier1_meta: Dict[str, Any],
    ai_analysis: Dict[str, Any],
    instant_view_url: Optional[str] = None,
    local_pdf_path: Optional[str] = None
) -> bool:
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "8929996006:AAEkcgtKYRJihNtDZUPxymvAEIDBIlWzqIc")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "5004771861")

    so_hieu = tier1_meta.get("doc_number", item["title"][:35])
    doc_type = tier1_meta.get("doc_type", "VĂN BẢN QUY PHẠM")
    authority = tier1_meta.get("authority", "Cơ quan ban hành")
    pub_date = item.get("published", datetime.now().strftime("%d/%m/%Y"))

    # Header
    msg = f"<b>📜 {doc_type} | TRẠM GÁC PHÁP LÝ 24/7</b>\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"📌 <b>Số hiệu:</b> <code>{so_hieu}</code>\n"
    msg += f"📅 <b>Ngày quét:</b> {pub_date} | 🏛️ <b>Cơ quan:</b> {authority}\n\n"

    # Top 3 điểm mới
    msg += f"🎯 <b>TOP ĐIỂM MỚI CỐT LÕI TÁC ĐỘNG HỒ SƠ:</b>\n"
    for pt in ai_analysis.get("summary_top3", [])[:3]:
        msg += f"• {pt}\n"
    msg += "\n"

    # Gói thầu bị ảnh hưởng
    packages = ai_analysis.get("affected_packages", [])
    if packages:
        msg += f"📦 <b>GÓI THẦU CẦN RÀ SOÁT NGAY:</b> <code>{', '.join(packages)}</code>\n\n"

    # Thẻ Căn Cứ 1-Chạm
    citation = ai_analysis.get("cau_can_cu_nd30", "")
    if citation:
        msg += f"📋 <b>THẺ CĂN CỨ 1-CHẠM (Chạm vào ô dưới để copy dán Word):</b>\n"
        msg += f"<code>{citation}</code>\n\n"

    # Sổ cái Excel
    msg += f"📊 <i>Sổ cái Excel Master đã tự động đồng bộ: <b>Kho_Can_Cu_Phap_Ly.xlsx</b></i>"

    # Nút bấm Inline
    buttons = []
    first_row = []
    if instant_view_url:
        first_row.append({"text": "📖 Đọc Báo cáo Instant View", "url": instant_view_url})
    if item.get("link"):
        first_row.append({"text": "🌐 Link Đối Soát Gốc", "url": item["link"]})
    if first_row:
        buttons.append(first_row)

    reply_markup = {"inline_keyboard": buttons} if buttons else None

    # Gửi tin nhắn text
    success = False
    send_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)

    try:
        with httpx.Client(timeout=15.0) as client:
            res = client.post(send_url, json=payload)
            if res.status_code == 200:
                success = True
                log(f"✅ Đã gửi thông báo Telegram thành công: {so_hieu}")
    except Exception as e:
        log(f"❌ Lỗi gửi tin nhắn Telegram: {e}")

    # Gửi đính kèm file PDF gốc có dấu mộc
    if local_pdf_path and os.path.exists(local_pdf_path):
        doc_url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
        caption = f"📎 File PDF gốc có chữ ký số/dấu mộc: {so_hieu}"
        try:
            with open(local_pdf_path, "rb") as f_pdf:
                with httpx.Client(timeout=60.0) as client:
                    files = {"document": (os.path.basename(local_pdf_path), f_pdf, "application/pdf")}
                    data = {"chat_id": chat_id, "caption": caption}
                    res = client.post(doc_url, data=data, files=files)
                    if res.status_code == 200:
                        log(f"✅ Đã gửi file PDF gốc đính kèm thành công: {local_pdf_path}")
        except Exception as e:
            log(f"⚠️ Lỗi gửi file PDF đính kèm Telegram: {e}")

    return success


def run_pipeline():
    log("🔍 BẮT ĐẦU CHU TRÌNH TRINH SÁT VÀ ĐỐI CHIẾU PHÁP LUẬT TỰ ĐỘNG (3-TIER FUNNEL)...")
    
    tier1_matcher = StructuralAuthorityMatcher()
    tier2_filter = SemanticDomainFilter()
    ai_analyzer = LegalAIAnalyzer()
    excel_sync = LegalExcelSyncEngine(EXCEL_LEGAL_PATH)
    telegraph_pub = TelegraphPublisher()

    known_docs = load_known_documents()
    total_matched = 0

    for source in FEED_SOURCES:
        log(f"📡 Đang quét nguồn: {source['name']} ({source['url']})...")
        try:
            with httpx.Client(timeout=30.0, follow_redirects=True, verify=False) as client:
                res = client.get(source["url"])
                if res.status_code != 200:
                    continue
                feed = feedparser.parse(res.text)
                log(f"   -> Đọc được {len(feed.entries)} mục tin mới nhất.")

                for entry in feed.entries:
                    raw_title = entry.get("title", "").strip()
                    link = normalize_url(source["url"], entry.get("link", ""))
                    summary = entry.get("summary", "").strip()
                    published = entry.get("published", datetime.now().strftime("%d/%m/%Y"))

                    doc_hash = hashlib.md5(f"{raw_title}_{link}".encode("utf-8")).hexdigest()
                    if doc_hash in known_docs:
                        continue

                    # =========================================================
                    # LỚP 1: BÓC TÁCH THỂ THỨC & THẨM QUYỀN (0.05ms)
                    # =========================================================
                    t1_res = tier1_matcher.process(raw_title, summary)
                    if not t1_res["is_valid_legal_doc"]:
                        known_docs.add(doc_hash)
                        continue

                    # =========================================================
                    # LỚP 2: BỘ LỌC NGỮ NGHĨA CHUYÊN NGÀNH SIÊU TỐC (3-5ms)
                    # =========================================================
                    t2_res = tier2_filter.process(raw_title, summary)
                    if not t2_res["is_domain_relevant"]:
                        known_docs.add(doc_hash)
                        continue

                    # =========================================================
                    # LỚP 3: BỘ NÃO GEMINI AI + PYDANTIC GROUNDING
                    # =========================================================
                    log(f"🎯 PHÁT HIỆN VĂN BẢN ĐÚNG CHUYÊN NGÀNH: {raw_title}")
                    
                    pdf_url = extract_direct_pdf_link(link)
                    local_pdf = None
                    if pdf_url:
                        local_pdf = download_official_pdf(pdf_url, doc_hash)

                    ai_result = ai_analyzer.analyze_document_deep(
                        doc_text=f"{raw_title}\n{summary}",
                        doc_title=raw_title,
                        doc_metadata=t1_res
                    )

                    # ĐỒNG BỘ SỔ CÁI EXCEL
                    excel_sync.sync_new_document(
                        so_hieu=t1_res.get("doc_number", raw_title[:30]),
                        loai_vb=t1_res.get("doc_type", "VĂN BẢN"),
                        co_quan=t1_res.get("authority", "GOV"),
                        ngay_bh=published,
                        ngay_hl=published,
                        linh_vuc=t2_res.get("best_matched_domain", "XÂY DỰNG"),
                        cau_can_cu=ai_result.get("cau_can_cu_nd30", ""),
                        tags_bo_sung=ai_result.get("affected_packages", [])
                    )

                    # XUẤT BẢN TELEGRAPH INSTANT VIEW
                    instant_url = None
                    try:
                        instant_url = telegraph_pub.publish_report(
                            title=f"BÁO CÁO PHÂN TÍCH: {t1_res.get('doc_number', raw_title[:40])}",
                            analysis_data=ai_result,
                            doc_item={"title": raw_title, "link": link}
                        )
                    except Exception:
                        pass

                    # BẮN TELEGRAM
                    item_data = {
                        "title": raw_title,
                        "link": link,
                        "published": published
                    }
                    send_telegram_alert(
                        item=item_data,
                        tier1_meta=t1_res,
                        ai_analysis=ai_result,
                        instant_view_url=instant_url,
                        local_pdf_path=local_pdf
                    )

                    known_docs.add(doc_hash)
                    total_matched += 1

        except Exception as e:
            log(f"❌ Lỗi khi quét nguồn {source['name']}: {e}")

    save_known_documents(known_docs)
    log(f"🏁 HOÀN THÀNH CHU TRÌNH TRINH SÁT. Số văn bản mới phù hợp: {total_matched}")


if __name__ == "__main__":
    run_pipeline()
