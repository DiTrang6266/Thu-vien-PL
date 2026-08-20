# -*- coding: utf-8 -*-
"""
HỆ THỐNG TRẠM GÁC & TRINH SÁT PHÁP LUẬT TỰ ĐỘNG 24/7 (AUTOMATED LEGAL RECON PIPELINE)
Kiến trúc Phễu 2 tầng:
- TẦNG 1: Sàng lọc thể thức & loại bỏ ngành ngoài/cá biệt (< 0.1ms) qua HybridTier2Classifier.
- TẦNG 2: AI Gatekeeper & Tóm tắt Trung thực Chống Ảo Giác qua LegalAIAnalyzer.
- TỰ ĐỘNG ĐỒNG BỘ: Xuất bản Telegraph Instant View, Đồng bộ Sổ cái Excel Master, Bắn tin nhắn Telegram 1-Tap Copy & Đính kèm PDF gốc.
"""

import os
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
import json
import re
import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin

import httpx
import feedparser
from bs4 import BeautifulSoup

from modules.classifier_tier1 import StructuralAuthorityMatcher, DocumentType
from modules.classifier_tier2 import HybridTier2Classifier, DomainEnum
from modules.ai_analyzer import LegalAIAnalyzer
from modules.excel_sync_engine import LegalExcelSyncEngine
from modules.telegraph_publisher import TelegraphPublisher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DOWNLOADS_DIR = os.path.join(DATA_DIR, "downloads")
KNOWN_DOCS_PATH = os.path.join(DATA_DIR, "known_documents.json")
EXCEL_LEGAL_PATH = os.path.join(DATA_DIR, "Kho_Can_Cu_Phap_Ly.xlsx")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8929996006:AAEkcgtKYRJihNtDZUPxymvAEIDBIlWzqIc")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "5004771861")

FEED_SOURCES = [
    {
        "name": "Công báo Nước CHXHCN Việt Nam (Văn bản mới)",
        "url": "https://congbao.chinhphu.vn/cac-van-ban-moi-ban-hanh.rss",
        "authority": "Chính phủ"
    },
    {
        "name": "Bộ Xây dựng (Văn bản quy phạm pháp luật mới)",
        "url": "https://moc.gov.vn/rss/1196/gioi-thieu-van-ban-moi.rss",
        "authority": "Bộ Xây dựng"
    },
    {
        "name": "Bộ Xây dựng (Chỉ đạo điều hành chuyên ngành)",
        "url": "https://moc.gov.vn/rss/1176/tin-chi-dao--dieu-hanh.rss",
        "authority": "Bộ Xây dựng"
    },
    {
        "name": "Bộ Kế hoạch và Đầu tư (Văn bản Đấu thầu & Đầu tư công)",
        "url": "https://www.mpi.gov.vn/Pages/rss.aspx",
        "authority": "Bộ Kế hoạch và Đầu tư"
    }
]


def log(msg: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {msg}"
    print(formatted)
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        log_file = os.path.join(DATA_DIR, "nhat_ky_trinh_sat.log")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception:
        pass


def load_known_documents() -> set:
    if os.path.exists(KNOWN_DOCS_PATH):
        try:
            with open(KNOWN_DOCS_PATH, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()


def save_known_documents(docs: set):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(KNOWN_DOCS_PATH, "w", encoding="utf-8") as f:
        json.dump(list(docs), f, ensure_ascii=False, indent=2)


def normalize_url(base_url: str, link: str) -> str:
    if not link:
        return ""
    link = link.strip()
    if link.startswith("http://") or link.startswith("https://"):
        return link
    if link.startswith("http:") and not link.startswith("http://"):
        link = link.replace("http:", "http://", 1)
    elif link.startswith("https:") and not link.startswith("https://"):
        link = link.replace("https:", "https://", 1)
    return urljoin(base_url, link)


def fetch_article_details(url: str) -> Dict[str, Any]:
    if not url:
        return {"body_text": "", "pdf_url": None}

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        with httpx.Client(timeout=20.0, follow_redirects=True, verify=False) as client:
            res = client.get(url, headers=headers)
            if res.status_code != 200:
                return {"body_text": "", "pdf_url": None}

            soup = BeautifulSoup(res.text, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()

            pdf_link = None
            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"].strip()
                if re.search(r"\.(pdf|docx|doc)($|\?)", href, re.IGNORECASE) or "download" in href.lower():
                    pdf_link = normalize_url(url, href)
                    break

            text_containers = soup.find_all(["div", "article", "section"], class_=re.compile(r"(content|detail|article|post|body)", re.IGNORECASE))
            if text_containers:
                body_text = "\n".join([c.get_text(separator="\n", strip=True) for c in text_containers])
            else:
                body_text = soup.get_text(separator="\n", strip=True)

            lines = [l.strip() for l in body_text.splitlines() if len(l.strip()) > 20]
            clean_text = "\n".join(lines[:100])
            return {"body_text": clean_text, "pdf_url": pdf_link}
    except Exception as e:
        log(f"⚠️ Không thể tải chi tiết URL {url}: {e}")
        return {"body_text": "", "pdf_url": None}


def download_official_pdf(pdf_url: str, doc_hash: str) -> Optional[str]:
    if not pdf_url:
        return None
    try:
        os.makedirs(DOWNLOADS_DIR, exist_ok=True)
        filename = f"{doc_hash[:16]}_van_ban_goc.pdf"
        file_path = os.path.join(DOWNLOADS_DIR, filename)

        if os.path.exists(file_path) and os.path.getsize(file_path) > 1000:
            return file_path

        headers = {"User-Agent": "Mozilla/5.0"}
        with httpx.Client(timeout=35.0, follow_redirects=True, verify=False) as client:
            res = client.get(pdf_url, headers=headers)
            if res.status_code == 200 and len(res.content) > 1000:
                with open(file_path, "wb") as f:
                    f.write(res.content)
                log(f"💾 Đã tải và lưu trữ file PDF thành công ({len(res.content)} bytes): {file_path}")
                return file_path
    except Exception as e:
        log(f"⚠️ Lỗi tải file PDF từ {pdf_url}: {e}")
    return None


def send_telegram_alert(
    item: Dict[str, Any],
    tier1_meta: Dict[str, Any],
    ai_analysis: Dict[str, Any],
    instant_view_url: Optional[str] = None,
    local_pdf_path: Optional[str] = None
):
    so_hieu = tier1_meta.get("doc_number", "MỚI")
    co_quan = tier1_meta.get("authority", "Bộ Xây dựng")
    ngay_ban_hanh = tier1_meta.get("ngay_ban_hanh", datetime.now().strftime("%d/%m/%Y"))
    title = item.get("title", "")
    cau_can_cu = ai_analysis.get("cau_can_cu_nd30", "")
    repealed_docs = ai_analysis.get("repealed_docs", [])
    summary_points = ai_analysis.get("summary_points", [])

    doc_type_str = str(tier1_meta.get("doc_type", "")).upper()
    if "VAN_BAN_HOP_NHAT" in doc_type_str or "VBHN" in title.upper() or "HỢP NHẤT" in title.upper():
        doc_type_label = "VĂN BẢN HỢP NHẤT"
    elif "QUYET_DINH" in doc_type_str:
        doc_type_label = "QUYẾT ĐỊNH"
    elif "NGHI_DINH" in doc_type_str:
        doc_type_label = "NGHỊ ĐỊNH"
    elif "LUAT" in doc_type_str:
        doc_type_label = "LUẬT"
    elif "QUY_CHUAN" in doc_type_str:
        doc_type_label = "QUY CHUẨN KỸ THUẬT"
    else:
        doc_type_label = "THÔNG TƯ"

    lines = [
        f"📑 <b>{doc_type_label} MỚI | {co_quan.upper()}</b>",
        f"<b>Số:</b> <code>{so_hieu}</code> • <b>Ban hành:</b> {ngay_ban_hanh}",
        f"━━━━━━━━━━━━━━━━━━━━━━",
        f"<b>{title.strip()}</b>",
        ""
    ]

    # Văn bản bãi bỏ nếu có
    if repealed_docs and len(repealed_docs) > 0:
        lines.append(f"🔴 <b>Bãi bỏ/Thay thế:</b> {', '.join(repealed_docs)}")
        lines.append("")

    # Quy định cốt lõi kèm trích dẫn Điều/Khoản
    lines.append("⚡ <b>QUY ĐỊNH CỐT LÕI (TRÍCH DẪN ĐIỀU KHOẢN):</b>")
    for pt in summary_points[:4]:
        lines.append(f"• {pt.replace('• ', '')}")

    lines.append("")
    lines.append("📋 <b>CHẠM ĐỂ COPY CĂN CỨ PHÁP LÝ (DÁN WORD):</b>")
    lines.append(f"<code>{cau_can_cu}</code>")

    lines.append("")
    lines.append("📊 <i>Sổ cái Excel Master đã tự động đồng bộ: Kho_Can_Cu_Phap_Ly.xlsx</i>")

    message_text = "\n".join(lines)

    inline_keyboard = []
    if instant_view_url:
        inline_keyboard.append([{"text": "📖 Đọc Báo cáo Toàn văn (Instant View)", "url": instant_view_url}])
    
    doc_link = item.get("link", "")
    if doc_link and doc_link.startswith("http"):
        inline_keyboard.append([{"text": "🌐 Link Văn Bản Gốc", "url": doc_link}])

    reply_markup = {"inline_keyboard": inline_keyboard} if inline_keyboard else None

    # Gửi tin nhắn
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message_text,
            "parse_mode": "HTML",
            "reply_markup": reply_markup
        }
        with httpx.Client(timeout=20.0) as client:
            res = client.post(url, json=payload)
            if res.status_code == 200:
                log(f"✅ Đã gửi thông báo Telegram thành công: {so_hieu}")
            else:
                log(f"⚠️ Gửi Telegram thất bại: {res.text}")
    except Exception as e:
        log(f"⚠️ Lỗi gửi Telegram: {e}")

    # Gửi file PDF đính kèm
    if local_pdf_path and os.path.exists(local_pdf_path):
        try:
            doc_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
            with open(local_pdf_path, "rb") as f:
                files = {"document": (os.path.basename(local_pdf_path), f, "application/pdf")}
                data = {
                    "chat_id": TELEGRAM_CHAT_ID,
                    "caption": f"📎 File PDF gốc: {so_hieu} ({title[:60]}...)"
                }
                with httpx.Client(timeout=45.0) as client:
                    doc_res = client.post(doc_url, data=data, files=files)
                    if doc_res.status_code == 200:
                        log(f"✅ Đã gửi file PDF gốc đính kèm thành công: {local_pdf_path}")
        except Exception as e:
            log(f"⚠️ Lỗi gửi file PDF Telegram: {e}")


def run_pipeline(force_reprocess: bool = False):
    log("🔍 BẮT ĐẦU CHU TRÌNH TRINH SÁT VÀ ĐỐI CHIẾU PHÁP LUẬT TỰ ĐỘNG (2-TIER HYBRID GATE)...")
    
    tier1_matcher = StructuralAuthorityMatcher()
    tier2_filter = HybridTier2Classifier()
    ai_analyzer = LegalAIAnalyzer()
    excel_sync = LegalExcelSyncEngine(EXCEL_LEGAL_PATH)
    telegraph_pub = TelegraphPublisher()

    known_docs = set() if force_reprocess else load_known_documents()
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
                    if not force_reprocess and doc_hash in known_docs:
                        continue

                    # TẦNG 1: SÀNG LỌC THỂ THỨC, NGÀNH NGOÀI & DỰ ÁN RIÊNG (< 0.1ms)
                    t2_res = tier2_filter.classify_and_filter(raw_title, summary)
                    if not t2_res["is_accepted"]:
                        log(f"ℹ️ Tầng 1 đã lọc bỏ ({t2_res['decision']}): {raw_title}")
                        known_docs.add(doc_hash)
                        continue

                    # CÀO NỘI DUNG CHI TIẾT
                    details = fetch_article_details(link)
                    body_text = details["body_text"]
                    pdf_url = details["pdf_url"]

                    # TẦNG 1 BÓC TÁCH METADATA
                    t1_res = tier1_matcher.process(raw_title, body_text, source_name=source["name"])
                    if not t1_res["is_valid_legal_doc"]:
                        known_docs.add(doc_hash)
                        continue

                    so_hieu_clean = t1_res.get("doc_number", raw_title[:35])
                    ngay_bh_clean = t1_res.get("ngay_ban_hanh", published)
                    auth_clean = t1_res.get("authority", source.get("authority", "Bộ Xây dựng"))

                    t1_res["raw_content"] = body_text[:2000]

                    # TẦNG 2: AI GATEKEEPER & TÓM TẮT TRUNG THỰC
                    ai_result = ai_analyzer.analyze_document_deep(
                        doc_text=f"{raw_title}\n{body_text[:5000]}",
                        doc_title=raw_title,
                        doc_metadata=t1_res
                    )

                    if not ai_result.get("is_project_relevant", True):
                        log(f"ℹ️ Tầng 2 AI đã lọc bỏ do không đạt yêu cầu chuyên môn/phạm vi: [{so_hieu_clean}] {raw_title}")
                        known_docs.add(doc_hash)
                        continue

                    log(f"🎯 PHÁT HIỆN VĂN BẢN PHỔ QUÁT TOÀN QUỐC HỢP LỆ: [{so_hieu_clean}] {raw_title}")

                    local_pdf = None
                    if pdf_url:
                        local_pdf = download_official_pdf(pdf_url, doc_hash)

                    # ĐỒNG BỘ SỔ CÁI EXCEL
                    excel_sync.sync_new_document(
                        so_hieu=so_hieu_clean,
                        loai_vb=t1_res.get("doc_type", "Thông tư"),
                        co_quan=auth_clean,
                        ngay_bh=ngay_bh_clean,
                        ngay_hl=ngay_bh_clean,
                        linh_vuc=str(t2_res.get("target_domain", "XÂY DỰNG")),
                        cau_can_cu=ai_result.get("cau_can_cu_nd30", "")
                    )

                    # XUẤT BẢN TELEGRAPH INSTANT VIEW
                    instant_url = None
                    try:
                        instant_url = telegraph_pub.publish_report(
                            title=f"TÓM TẮT VĂN BẢN: {so_hieu_clean}",
                            analysis_data=ai_result,
                            doc_item={
                                "so_hieu": so_hieu_clean,
                                "co_quan": auth_clean,
                                "ngay_ban_hanh": ngay_bh_clean,
                                "link": link
                            }
                        )
                    except Exception as e:
                        log(f"⚠️ Lỗi xuất bản Telegraph: {e}")

                    # BẮN TELEGRAM
                    item_data = {
                        "title": raw_title,
                        "link": link,
                        "published": ngay_bh_clean
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
