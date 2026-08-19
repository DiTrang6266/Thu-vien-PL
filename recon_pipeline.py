#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
HỆ THỐNG TRINH SÁT PHÁP LUẬT TỰ ĐỘNG (LEGAL RECONNAISSANCE ENGINE)
Chuyên ngành: Xây dựng, Đấu thầu, Quản lý chi phí và Đầu tư công Việt Nam
Tác giả: Tự động hóa Hồ sơ Dự án
=============================================================================
"""

import os
import sys
import json
import re
import hashlib
from datetime import datetime
import feedparser
import httpx
from bs4 import BeautifulSoup
import urllib3

# Tắt cảnh báo SSL cho các cổng thông tin công vụ
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Đường dẫn thư mục dữ liệu
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATABASE_FILE = os.path.join(DATA_DIR, "known_documents.json")
LOG_FILE = os.path.join(DATA_DIR, "nhat_ky_trinh_sat.log")

# Cấu hình Token Telegram (Ưu tiên lấy từ biến môi trường, fallback về mã mặc định của anh Duy)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8929996006:AAEkcgtKYRJihNtDZUPxymvAEIDBIlWzqIc")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "5004771861")

# Danh sách nguồn cấp tin chính thức của Nhà nước (RSS Feeds)
RSS_SOURCES = [
    {
        "name": "Công báo Nước CHXHCN Việt Nam",
        "url": "https://congbao.chinhphu.vn/cac-van-ban-moi-ban-hanh.rss",
        "type": "CONG_BAO"
    },
    {
        "name": "Bộ Xây dựng - Văn bản mới",
        "url": "https://moc.gov.vn/rss/1196/gioi-thieu-van-ban-moi.rss",
        "type": "BO_XAY_DUNG"
    },
    {
        "name": "Bộ Xây dựng - Chỉ đạo điều hành",
        "url": "https://moc.gov.vn/rss/1176/tin-chi-dao--dieu-hanh.rss",
        "type": "BO_XAY_DUNG_CHIDAO"
    }
]

# Bộ lọc từ khóa chuyên ngành Xây dựng, Đấu thầu và Đầu tư công
KEYWORD_RULES = {
    "DAU_THAU": [
        r"đấu thầu", r"lựa chọn nhà thầu", r"chỉ định thầu", r"e-hsmt", r"e-hsyc",
        r"kế hoạch lựa chọn nhà thầu", r"mạng đấu thầu", r"bảo lãnh dự thầu",
        r"luật đấu thầu", r"nghị định 24/2024", r"thông tư 06/2024", r"thông tư 08/2022"
    ],
    "QUAN_LY_CHI_PHI": [
        r"định mức dự toán", r"đơn giá nhân công", r"giá ca máy", r"chỉ số giá xây dựng",
        r"quản lý chi phí", r"tổng mức đầu tư", r"dự toán xây dựng", r"nghị định 10/2021",
        r"thông tư 11/2021", r"thông tư 12/2021", r"thông tư 13/2021", r"thông tư 14/2023",
        r"chi phí quản lý dự án", r"chi phí tư vấn", r"suất vốn đầu tư"
    ],
    "DAU_TU_CONG": [
        r"đầu tư công", r"luật đầu tư công", r"vốn ngân sách", r"quyết toán dự án",
        r"tạm ứng hợp đồng", r"nghị định 99/2021", r"thông tư 96/2021", r"báo cáo nghiên cứu khả thi",
        r"báo cáo kinh tế - kỹ thuật", r"nghị định 15/2021", r"nghị định 35/2023"
    ],
    "CHAT_LUONG_PCCC": [
        r"quản lý chất lượng", r"nghiệm thu hoàn thành", r"phòng cháy chữa cháy",
        r"thẩm duyệt pccc", r"qcvn", r"tcvn", r"giấy phép xây dựng", r"an toàn lao động",
        r"quy chuẩn kỹ thuật"
    ]
}

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

def classify_document(title: str, summary: str) -> list:
    combined_text = f"{title} {summary}".lower()
    matched_categories = []
    for cat, patterns in KEYWORD_RULES.items():
        for pattern in patterns:
            if re.search(pattern, combined_text, re.IGNORECASE):
                matched_categories.append(cat)
                break
    return matched_categories

def send_telegram_alert(item: dict) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        log("ℹ️ Không tìm thấy Token Telegram. Bỏ qua bước gửi tin nhắn.")
        return False

    cat_labels = {
        "DAU_THAU": "🏷️ Đấu thầu & Lựa chọn nhà thầu",
        "QUAN_LY_CHI_PHI": "💰 Quản lý chi phí & Định mức dự toán",
        "DAU_TU_CONG": "🏛️ Đầu tư công & Ngân sách",
        "CHAT_LUONG_PCCC": "🛡️ Quản lý chất lượng & PCCC"
    }

    cats_str = "\n".join([f"• {cat_labels.get(c, c)}" for c in item.get("categories", [])])

    message_text = (
        f"🏛 <b>[PHÁT HIỆN VĂN BẢN XÂY DỰNG MỚI]</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📄 <b>Tiêu đề:</b> {item['title']}\n"
        f"🏢 <b>Nguồn cấp:</b> {item['source_name']}\n"
        f"📅 <b>Ngày phát hiện:</b> {item.get('published', 'Vừa cập nhật')}\n\n"
        f"📂 <b>Lĩnh vực liên quan:</b>\n{cats_str}\n\n"
        f"📝 <b>Trích yếu tóm tắt:</b>\n"
        f"<i>{item.get('summary', 'Nhấn link bên dưới để xem toàn văn')}</i>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔗 <a href='{item['link']}'>👉 Xem toàn văn & Tải file PDF bản gốc</a>"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message_text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }

    try:
        response = httpx.post(url, json=payload, timeout=15)
        if response.status_code == 200:
            log(f"✅ Đã gửi thông báo Telegram thành công: {item['title'][:60]}...")
            return True
        else:
            log(f"❌ Gửi Telegram thất bại ({response.status_code}): {response.text}")
            return False
    except Exception as e:
        log(f"❌ Lỗi kết nối Telegram: {e}")
        return False

def run_reconnaissance() -> int:
    init_storage()
    known_docs = load_known_documents()
    new_matched_count = 0

    log("🔍 BẮT ĐẦU CHU TRÌNH TRINH SÁT VĂN BẢN PHÁP LUẬT...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    with httpx.Client(verify=False, headers=headers, follow_redirects=True, timeout=25.0) as client:
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

                    categories = classify_document(title, summary)

                    if categories:
                        log(f"🎯 PHÁT HIỆN VĂN BẢN ĐÚNG NGÀNH: {title}")
                        doc_item = {
                            "id": doc_hash,
                            "title": title,
                            "link": link,
                            "summary": summary[:400] + ("..." if len(summary) > 400 else ""),
                            "published": published,
                            "source_name": source["name"],
                            "categories": categories,
                            "discovered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        send_telegram_alert(doc_item)
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
