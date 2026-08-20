# -*- coding: utf-8 -*-
"""
Hệ thống Trinh sát & Đối chiếu Văn bản Pháp luật 24/7 (Zero-Cost Watchdog Engine)
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

# Load environment variables from .env
env_local = os.path.join(BASE_DIR, ".env")
if os.path.exists(env_local):
    with open(env_local, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip()

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

FEED_SOURCES = [
    {
        "name": "Công báo Nước CHXHCN Việt Nam (Văn bản mới)",
        "url": "https://congbao.chinhphu.vn/cac-van-ban-moi-ban-hanh.rss",
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

DOC_TYPE_LABELS = {
    "THONG_TU": "THÔNG TƯ",
    "NGHI_DINH": "NGHỊ ĐỊNH",
    "LUAT": "LUẬT",
    "QUYET_DINH": "QUYẾT ĐỊNH",
    "VAN_BAN_HOP_NHAT": "VĂN BẢN HỢP NHẤT",
    "QUY_CHUAN": "QUY CHUẨN KỸ THUẬT QUỐC GIA (QCVN)",
    "TIEU_CHUAN": "TIÊU CHUẨN QUỐC GIA (TCVN)",
    "NGHI_QUYET": "NGHỊ QUYẾT",
    "CONG_VAN": "CÔNG VĂN"
}


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


def fetch_article_details(article_url: str) -> Dict[str, Any]:
    body_text = ""
    pdf_url = None
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://vanban.chinhphu.vn/"
        }
        with httpx.Client(timeout=15.0, headers=headers, follow_redirects=True, verify=False) as client:
            res = client.get(article_url)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                body_text = soup.get_text(separator=" ", strip=True)
                for a in soup.find_all("a", href=True):
                    href = a["href"].strip()
                    if ".pdf" in href.lower() or "download" in href.lower() or "file_name=" in href.lower():
                        pdf_url = normalize_url(article_url, href)
                        break
    except Exception:
        pass
    return {"body_text": body_text, "pdf_url": pdf_url}


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
    raw_doc_type = tier1_meta.get("doc_type", "THONG_TU")
    doc_type_label = DOC_TYPE_LABELS.get(raw_doc_type, "VĂN BẢN QUY PHẠM PHÁP LUẬT")
    authority = tier1_meta.get("authority", "Bộ Xây dựng")
    pub_date = item.get("published", datetime.now().strftime("%d/%m/%Y"))

    # Header
    msg = f"<b>📜 {doc_type_label} | TRẠM GÁC PHÁP LÝ 24/7</b>\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"📌 <b>Số hiệu:</b> <code>{so_hieu}</code>\n"
    msg += f"📅 <b>Ngày ban hành:</b> {pub_date} | 🏛️ <b>Cơ quan:</b> {authority}\n\n"

    # Nội dung tóm tắt trung thực
    msg += f"🎯 <b>NỘI DUNG TÓM TẮT TRUNG THỰC (BÁM SÁT VĂN BẢN):</b>\n"
    points = ai_analysis.get("summary_points", [])
    if not points:
        points = ai_analysis.get("summary_top3", [])
    for pt in points[:4]:
        msg += f"{pt}\n"
    msg += "\n"

    # Văn bản bãi bỏ / thay thế nếu có
    repealed = ai_analysis.get("repealed_docs", [])
    if repealed and isinstance(repealed, list) and len(repealed) > 0:
        msg += f"❌ <b>Văn bản bị bãi bỏ / thay thế:</b>\n"
        for r in repealed[:3]:
            msg += f"• {r}\n"
        msg += "\n"

    # Thẻ Căn Cứ 1-Chạm
    citation = ai_analysis.get("cau_can_cu_nd30", "")
    if citation:
        msg += f"📋 <b>THẺ CĂN CỨ 1-CHẠM (Chạm vào ô dưới để copy dán Word):</b>\n"
        msg += f"<code>{citation}</code>\n\n"

    # Sổ cái Excel
    msg += f"📊 <i>Sổ cái Excel Master đã tự động đồng bộ: <b>Kho_Can_Cu_Phap_Ly.xlsx</b></i>"

    # Nút bấm Inline (Instant View & Link gốc)
    buttons = []
    if instant_view_url:
        buttons.append([{"text": "📖 ĐỌC BÁO CÁO TÓM TẮT TOÀN VĂN (INSTANT VIEW)", "url": instant_view_url}])
    if item.get("link"):
        buttons.append([{"text": "🌐 Link Đối Soát Gốc", "url": item["link"]}])

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
        with httpx.Client(timeout=15.0, verify=False) as client:
            res = client.post(send_url, json=payload)
            if res.status_code == 200:
                success = True
                log(f"✅ Đã gửi thông báo Telegram thành công: {so_hieu}")
    except Exception as e:
        log(f"❌ Lỗi gửi tin nhắn Telegram: {e}")

    # Gửi đính kèm file PDF gốc
    if local_pdf_path and os.path.exists(local_pdf_path):
        doc_url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
        caption = f"📎 File PDF gốc có chữ ký số/dấu mộc: {so_hieu}"
        try:
            with open(local_pdf_path, "rb") as f_pdf:
                with httpx.Client(timeout=60.0, verify=False) as client:
                    files = {"document": (os.path.basename(local_pdf_path), f_pdf, "application/pdf")}
                    data = {"chat_id": chat_id, "caption": caption}
                    res = client.post(doc_url, data=data, files=files)
                    if res.status_code == 200:
                        log(f"✅ Đã gửi file PDF gốc đính kèm thành công: {local_pdf_path}")
        except Exception as e:
            log(f"⚠️ Lỗi gửi file PDF đính kèm Telegram: {e}")

    return success


def run_pipeline(force_reprocess: bool = False):
    log("🔍 BẮT ĐẦU CHU TRÌNH TRINH SÁT VÀ ĐỐI CHIẾU PHÁP LUẬT TỰ ĐỘNG (3-TIER FUNNEL)...")
    
    tier1_matcher = StructuralAuthorityMatcher()
    tier2_filter = SemanticDomainFilter()
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

                    # LỚP 2: BỘ LỌC NGỮ NGHĨA CHUYÊN NGÀNH & PHẠM VI ÁP DỤNG
                    t2_res = tier2_filter.process(raw_title, summary)
                    if not t2_res["is_domain_relevant"]:
                        if t2_res.get("best_matched_domain") == "VAN_BAN_DAC_THU_DU_AN_RIENG":
                            log(f"ℹ️ Lớp 2 đã lọc bỏ văn bản đặc thù cho 1 dự án riêng: {raw_title}")
                        known_docs.add(doc_hash)
                        continue

                    # CÀO NỘI DUNG CHI TIẾT
                    details = fetch_article_details(link)
                    body_text = details["body_text"]
                    pdf_url = details["pdf_url"]

                    # LỚP 1: BÓC TÁCH THỂ THỨC & THẨM QUYỀN
                    t1_res = tier1_matcher.process(raw_title, body_text, source_name=source["name"])
                    if not t1_res["is_valid_legal_doc"]:
                        known_docs.add(doc_hash)
                        continue

                    so_hieu_clean = t1_res.get("doc_number", raw_title[:35])
                    ngay_bh_clean = t1_res.get("ngay_ban_hanh", published)
                    auth_clean = t1_res.get("authority", "Bộ Xây dựng")

                    t1_res["raw_content"] = body_text[:2000]
                    ai_result = ai_analyzer.analyze_document_deep(
                        doc_text=f"{raw_title}\n{body_text[:5000]}",
                        doc_title=raw_title,
                        doc_metadata=t1_res
                    )

                    # KIỂM TRA PHẠM VI ÁP DỤNG CỦA AI
                    if not ai_result.get("is_project_relevant", True) or not ai_result.get("is_nationwide_universal", True):
                        log(f"ℹ️ AI đã lọc bỏ văn bản do phạm vi không áp dụng toàn quốc: [{so_hieu_clean}] {raw_title}")
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
                        linh_vuc=t2_res.get("best_matched_domain", "XÂY DỰNG"),
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
