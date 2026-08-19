#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
HỆ THỐNG TRINH SÁT & ĐỐI CHIẾU PHÁP LUẬT TỰ ĐỘNG 100% (ZERO-TOUCH LEGAL RECON)
Phân loại chuẩn hóa theo Luật Ban hành VBQPPL:
1. LUẬT & NGHỊ QUYẾT QUỐC HỘI
2. NGHỊ ĐỊNH & QUYẾT ĐỊNH CHÍNH PHỦ / THỦ TƯỚNG
3. THÔNG TƯ (BXD, BKHĐT, BTC, BQP...)
4. VĂN BẢN HƯỚNG DẪN, CÔNG VĂN & QUY CHUẨN KỸ THUẬT (QCVN/TCVN)
=============================================================================
"""

import os
import sys
import json
import re
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import feedparser
import httpx
from bs4 import BeautifulSoup
import urllib3

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from modules.legal_parser import LegalDocumentParser
from modules.legal_diff import LegalDocumentDiffer
from modules.ai_analyzer import LegalAIAnalyzer
from modules.telegraph_publisher import TelegraphPublisher

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DOWNLOAD_DIR = os.path.join(DATA_DIR, "downloads")
DATABASE_FILE = os.path.join(DATA_DIR, "known_documents.json")
LOG_FILE = os.path.join(DATA_DIR, "nhat_ky_trinh_sat.log")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8929996006:AAEkcgtKYRJihNtDZUPxymvAEIDBIlWzqIc")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "5004771861")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

RSS_SOURCES = [
    {
        "name": "Công báo Nước CHXHCN Việt Nam (Văn bản mới)",
        "url": "https://congbao.chinhphu.vn/cac-van-ban-moi-ban-hanh.rss",
        "type": "CONG_BAO_VAN_BAN"
    },
    {
        "name": "Công báo Nước CHXHCN Việt Nam (Số mới đăng)",
        "url": "http://congbao.chinhphu.vn/cac-so-cong-bao-moi-dang.rss",
        "type": "CONG_BAO_SO_DANG"
    },
    {
        "name": "Bộ Xây dựng (Văn bản quy phạm pháp luật mới)",
        "url": "https://moc.gov.vn/rss/1196/gioi-thieu-van-ban-moi.rss",
        "type": "BO_XAY_DUNG_QPPL"
    },
    {
        "name": "Bộ Xây dựng (Chỉ đạo điều hành chuyên ngành)",
        "url": "https://moc.gov.vn/rss/1176/tin-chi-dao--dieu-hanh.rss",
        "type": "BO_XAY_DUNG_CHIDAO"
    },
    {
        "name": "Bộ Kế hoạch và Đầu tư (Văn bản Đấu thầu & Đầu tư công)",
        "url": "https://www.mpi.gov.vn/Pages/rss.aspx",
        "type": "BO_KE_HOACH_DAU_TU"
    }
]

# BỘ LỌC CHUYÊN NGÀNH: XÂY DỰNG, ĐẤU THẦU QUA MẠNG, ĐẦU TƯ CÔNG, CHI THƯỜNG XUYÊN, DOANH TRẠI BQP
DOMAIN_KEYWORDS = [
    r"đấu thầu", r"lựa chọn nhà thầu", r"chỉ định thầu", r"mạng đấu thầu", r"muasamcong",
    r"e-hsmt", r"e-hsdt", r"e-tbmt", r"e-hsyc", r"e-hsdx", r"bảo lãnh dự thầu",
    r"quản lý chi phí", r"định mức dự toán", r"đơn giá nhân công", r"giá ca máy",
    r"chi phí quản lý dự án", r"chi phí tư vấn", r"suất vốn đầu tư", r"hợp đồng xây dựng",
    r"đầu tư công", r"quản lý dự án", r"báo cáo nghiên cứu khả thi", r"báo cáo kinh tế - kỹ thuật",
    r"thiết kế bản vẽ thi công", r"bvtc", r"thẩm tra thiết kế", r"thẩm tra dự toán",
    r"thẩm định thiết kế", r"thẩm định dự toán", r"tư vấn giám sát", r"thi công xây dựng",
    r"nhật ký thi công", r"bản vẽ hoàn công", r"nghiệm thu hoàn thành", r"quyết toán dự án",
    r"kiểm toán độc lập", r"bảo hiểm công trình", r"thí nghiệm nén tĩnh cọc",
    r"chi thường xuyên", r"kinh phí thường xuyên", r"tài sản công", r"sửa chữa bảo trì",
    r"bộ quốc phòng", r"tt-bqp", r"doanh trại", r"doanh cụ", r"công tác doanh trại",
    r"quân chủng pk-kq", r"công trình quân sự", r"định mức doanh cụ",
    r"quản lý chất lượng", r"phòng cháy chữa cháy", r"pccc", r"qcvn", r"tcvn"
]


def log(msg: str):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_msg = f"[{now_str}] {msg}"
    print(formatted_msg)
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted_msg + "\n")
    except Exception:
        pass


def init_storage():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    if not os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=2)


def load_known_documents() -> dict:
    try:
        with open(DATABASE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_known_documents(data: dict):
    with open(DATABASE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def clean_html_text(raw_html: str) -> str:
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text(separator=" ").strip()
    return re.sub(r"\s+", " ", text)


def normalize_url(link: str) -> str:
    link = link.strip()
    if link.startswith("http:moc.gov.vn"):
        link = link.replace("http:moc.gov.vn", "https://moc.gov.vn")
    elif link.startswith("http:") and not link.startswith("http://"):
        link = link.replace("http:", "https://")
    elif link.startswith("/"):
        link = "https://moc.gov.vn" + link
    elif not link.startswith("http://") and not link.startswith("https://"):
        link = "https://" + link
    return link


def is_relevant_document(title: str, summary: str) -> bool:
    combined_text = f"{title} {summary}".lower()
    for pattern in DOMAIN_KEYWORDS:
        if re.search(pattern, combined_text, re.IGNORECASE):
            return True
    return False


def classify_document_type(title: str) -> Tuple[str, str]:
    """
    Phân loại chuẩn hóa theo đúng 4 nhóm hình thức văn bản pháp lý:
    1. LUẬT / NGHỊ QUYẾT QUỐC HỘI
    2. NGHỊ ĐỊNH / QUYẾT ĐỊNH CHÍNH PHỦ
    3. THÔNG TƯ
    4. VĂN BẢN HƯỚNG DẪN / CÔNG VĂN / QUY CHUẨN
    """
    title_lower = title.lower()

    if re.search(r"\bluật\b|\bbộ luật\b|nghị quyết.*quốc hội|/qh", title_lower):
        return ("🏛️ LUẬT & NGHỊ QUYẾT QUỐC HỘI", "LUAT")
    
    if re.search(r"\bnghị định\b|/nđ-cp|\bquyết định.*thủ tướng|/qđ-ttg", title_lower):
        return ("📜 NGHỊ ĐỊNH & QUYẾT ĐỊNH CHÍNH PHỦ", "NGHI_DINH")
    
    if re.search(r"\bthông tư\b|/tt-|/vbhn-", title_lower):
        if "bqp" in title_lower or "quốc phòng" in title_lower:
            return ("🎖️ THÔNG TƯ BỘ QUỐC PHÒNG", "THONG_TU_BQP")
        return ("📑 THÔNG TƯ CÁC BỘ (BXD, BKHĐT, BTC...)", "THONG_TU")
    
    if re.search(r"\bqcvn\b|\btcvn\b|quy chuẩn|tiêu chuẩn", title_lower):
        return ("📐 QUY CHUẨN & TIÊU CHUẨN KỸ THUẬT", "QUY_CHUAN")

    return ("📌 VĂN BẢN HƯỚNG DẪN, CHỈ ĐẠO & CÔNG VĂN", "HUONG_DAN")


def extract_and_download_pdf(doc_url: str, doc_id: str) -> Optional[str]:
    clean_url = normalize_url(doc_url)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": clean_url
    }

    try:
        with httpx.Client(verify=False, headers=headers, follow_redirects=True, timeout=25.0) as client:
            resp = client.get(clean_url)
            if resp.status_code != 200:
                return None

            soup = BeautifulSoup(resp.text, "html.parser")
            pdf_link = None

            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"].strip()
                if ".pdf" in href.lower() or "datafiles.chinhphu.vn" in href.lower():
                    pdf_link = href
                    break

            if not pdf_link:
                return None

            pdf_url = normalize_url(pdf_link)
            log(f"📥 Tìm thấy link PDF gốc: {pdf_url}")

            pdf_resp = client.get(pdf_url)
            if pdf_resp.status_code == 200 and len(pdf_resp.content) > 1000:
                clean_filename = f"{doc_id[:16]}_van_ban_goc.pdf"
                save_path = os.path.join(DOWNLOAD_DIR, clean_filename)
                with open(save_path, "wb") as f:
                    f.write(pdf_resp.content)
                log(f"💾 Đã tải và lưu trữ file PDF thành công ({len(pdf_resp.content)} bytes): {save_path}")
                return save_path

    except Exception as e:
        log(f"⚠️ Không thể tự động tải PDF từ {clean_url}: {e}")

    return None


def send_telegram_document(pdf_path: str, caption: str) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    try:
        with open(pdf_path, "rb") as f:
            files = {"document": (os.path.basename(pdf_path), f, "application/pdf")}
            data = {
                "chat_id": TELEGRAM_CHAT_ID,
                "caption": caption[:1024],
                "parse_mode": "HTML"
            }
            res = httpx.post(url, data=data, files=files, timeout=40.0)
            return res.status_code == 200
    except Exception as e:
        log(f"❌ Lỗi gửi file PDF qua Telegram: {e}")
        return False


def process_and_send_alert(item: dict, ai_analyzer: LegalAIAnalyzer, telegraph_pub: TelegraphPublisher) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        log("ℹ️ Không tìm thấy Token Telegram. Bỏ qua bước gửi tin nhắn.")
        return False

    type_label, type_code = classify_document_type(item["title"])
    clean_link = normalize_url(item["link"])

    pdf_file_path = extract_and_download_pdf(clean_link, item.get("id", "doc"))

    log(f"🧠 Đang gọi AI Gemini phân tích tác động pháp lý cho: {item['title'][:60]}...")
    doc_meta = {
        "so_hieu": item["title"],
        "co_quan": item["source_name"],
        "loai_van_ban": type_label,
        "ngay_ban_hanh": item.get("published", datetime.now().strftime("%d/%m/%Y"))
    }
    
    ai_data = ai_analyzer.analyze_legal_impact(
        old_doc_text=item.get("old_text", item.get("summary", "")),
        new_doc_text=f"{item['title']}\n{item.get('new_text', item.get('summary', ''))}",
        doc_metadata=doc_meta
    )

    telegraph_url = telegraph_pub.publish_report(
        title=f"BÁO CÁO PHÂN TÍCH: {item['title']}",
        ai_data=ai_data,
        doc_meta=doc_meta
    )

    top3_bullets = "\n".join(ai_data.get("summary_top3", ["Đã hoàn thành rà soát và đối chiếu toàn văn."]))
    
    # CẤU TRÚC TIN NHẮN CHUẨN HÓA RÕ RÀNG
    message_text = (
        f"🏛 <b>[TRINH SÁT PHÁP LÝ: PHÁT HIỆN VĂN BẢN MỚI]</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📂 <b>Phân loại:</b> <b>{type_label}</b>\n"
        f"📄 <b>Văn bản:</b> {item['title']}\n"
        f"🏢 <b>Cơ quan ban hành:</b> {item['source_name']}\n"
        f"📅 <b>Thời gian:</b> {item.get('published', 'Vừa cập nhật')}\n\n"
        f"🌟 <b>Top điểm cốt lõi thay đổi:</b>\n"
        f"<i>{top3_bullets}</i>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👇 <b>Bấm nút bên dưới để ĐỌC TOÀN VĂN BÁO CÁO (Instant View):</b>"
    )

    inline_buttons = []
    if telegraph_url:
        inline_buttons.append([
            {"text": "📖 ĐỌC BÁO CÁO PHÂN TÍCH TOÀN VĂN (INSTANT VIEW)", "url": telegraph_url}
        ])
    
    inline_buttons.append([
        {"text": "🌐 XEM BÀI VIẾT NGUỒN CHÍNH THỨC", "url": clean_link}
    ])

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message_text,
        "parse_mode": "HTML",
        "reply_markup": {
            "inline_keyboard": inline_buttons
        }
    }

    sent_msg = False
    try:
        response = httpx.post(url, json=payload, timeout=20)
        if response.status_code == 200:
            log(f"✅ Đã gửi thông báo Telegram kèm Instant View thành công: {item['title'][:60]}...")
            sent_msg = True
        else:
            log(f"❌ Gửi Telegram thất bại ({response.status_code}): {response.text}")
    except Exception as e:
        log(f"❌ Lỗi kết nối Telegram: {e}")

    if pdf_file_path and os.path.exists(pdf_file_path):
        caption_text = f"📑 <b>File PDF gốc có dấu đỏ/chữ ký số:</b>\n<i>{item['title'][:200]}</i>"
        send_telegram_document(pdf_file_path, caption_text)

    return sent_msg


def run_reconnaissance() -> int:
    init_storage()
    known_docs = load_known_documents()
    new_matched_count = 0

    log("🔍 BẮT ĐẦU CHU TRÌNH TRINH SÁT VÀ ĐỐI CHIẾU PHÁP LUẬT TỰ ĐỘNG...")
    
    ai_analyzer = LegalAIAnalyzer(api_key=GEMINI_API_KEY)
    telegraph_pub = TelegraphPublisher()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    with httpx.Client(verify=False, headers=headers, follow_redirects=True, timeout=30.0) as client:
        for source in RSS_SOURCES:
            log(f"📡 Đang quét nguồn: {source['name']} ({source['url']})...")
            try:
                resp = client.get(source["url"])
                if resp.status_code != 200:
                    log(f"⚠️ Nguồn {source['name']} phản hồi mã {resp.status_code}. Bỏ qua.")
                    continue

                feed = feedparser.parse(resp.text)
                log(f"   -> Đọc được {len(feed.entries)} mục tin mới nhất.")

                for entry in feed.entries:
                    link = entry.get("link", "").strip()
                    title = entry.get("title", "").strip()
                    raw_summary = entry.get("summary", entry.get("description", "")).strip()
                    summary = clean_html_text(raw_summary)
                    published = entry.get("published", entry.get("updated", "")).strip()

                    if not link or not title:
                        continue

                    doc_hash = hashlib.md5(link.encode("utf-8")).hexdigest()

                    if doc_hash in known_docs:
                        continue

                    if is_relevant_document(title, summary):
                        log(f"🎯 PHÁT HIỆN VĂN BẢN ĐÚNG NGÀNH: {title}")
                        doc_item = {
                            "id": doc_hash,
                            "title": title,
                            "link": link,
                            "summary": summary,
                            "published": published,
                            "source_name": source["name"],
                            "discovered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        process_and_send_alert(doc_item, ai_analyzer, telegraph_pub)
                        
                        known_docs[doc_hash] = doc_item
                        new_matched_count += 1
                    else:
                        known_docs[doc_hash] = {
                            "title": title,
                            "filtered_out": True,
                            "discovered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }

            except Exception as e:
                log(f"❌ Lỗi khi quét nguồn {source['name']}: {e}")

    save_known_documents(known_docs)
    log(f"🏁 HOÀN THÀNH CHU TRÌNH TRINH SÁT. Số văn bản mới phù hợp: {new_matched_count}")
    return new_matched_count


if __name__ == "__main__":
    run_reconnaissance()
