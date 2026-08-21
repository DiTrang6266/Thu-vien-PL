#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
HỆ THỐNG TRINH SÁT & ĐỐI CHIẾU PHÁP LUẬT TỰ ĐỘNG 100% (ZERO-TOUCH LEGAL RECON)
Kiến trúc Lọc Đa Tầng Thông Minh (3-Tier Intelligent Cascade Filtering)
Chuẩn hóa Mẫu Hiển Thị Master Template cho Telegram & Telegraph Instant View
- Tầng 1: Fast Heuristics & Blacklist Regex (0đ, <1ms)
- Tầng 2: Gemini AI Gatekeeper Triage (0.3s, ~30 tokens)
- Tầng 3: Deep Redline & Impact Analysis (Master Template + All-in-One Delivery)
Bản quyền & Thiết kế: Tự động hóa Hồ sơ Dự án
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
from modules.ai_gatekeeper import LegalGatekeeper
from modules.telegraph_publisher import TelegraphPublisher
from modules.legal_db_sync import sync_legal_document_to_excel

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

# TẦNG 1A: DANH SÁCH TỪ KHÓA CẤM (BLACKLIST CHẶN RÁC NGAY VÒNG 1)
HARD_EXCLUDE_PATTERNS = [
    r"thuốc biệt dược", r"generic nhóm", r"vật tư tiêu hao y tế", r"hóa chất xét nghiệm",
    r"sinh phẩm chẩn đoán", r"đấu thầu thuốc", r"mua sắm thuốc",
    r"xây dựng đảng", r"chỉnh đốn đảng", r"công tác cán bộ", r"phát triển đảng viên",
    r"tổ chức đoàn thể", r"công đoàn cơ sở", r"huân chương lao động", r"bằng khen của thủ tướng",
    r"bổ nhiệm giữ chức vụ", r"miễn nhiệm chức vụ", r"kỷ luật cảnh cáo",
    r"tuyển sinh đại học", r"thi tốt nghiệp thpt", r"giống cây trồng", r"chăn nuôi lợn",
    r"khai thác hải sản", r"cấp phép thăm dò khoáng sản", r"xử phạt giao thông"
]

# TẦNG 1B: BỘ TỪ KHÓA ĐỊNH HƯỚNG CHUYÊN NGÀNH MỞ RỘNG (WHITELIST GỐC & GHÉP)
DOMAIN_KEYWORDS = [
    r"\bxây dựng\b", r"\bđấu thầu\b", r"lựa chọn nhà thầu", r"chỉ định thầu", r"mạng đấu thầu", r"muasamcong",
    r"e-hsmt", r"e-hsdt", r"e-tbmt", r"e-hsyc", r"e-hsdx", r"bảo lãnh dự thầu",
    r"quản lý chi phí", r"định mức dự toán", r"\bdự toán\b", r"đơn giá nhân công", r"giá ca máy",
    r"chi phí quản lý dự án", r"chi phí tư vấn", r"suất vốn đầu tư", r"hợp đồng xây dựng",
    r"đầu tư công", r"quản lý dự án", r"báo cáo nghiên cứu khả thi", r"báo cáo kinh tế - kỹ thuật",
    r"thiết kế bản vẽ thi công", r"\bbvtc\b", r"\bthiết kế\b", r"\bkhảo sát\b",
    r"thẩm tra thiết kế", r"thẩm tra dự toán", r"\bthẩm tra\b", r"\bthẩm định\b",
    r"thẩm định thiết kế", r"thẩm định dự toán", r"tư vấn giám sát", r"\bgiám sát\b",
    r"thi công xây dựng", r"\bthi công\b", r"nhật ký thi công", r"bản vẽ hoàn công",
    r"nghiệm thu hoàn thành", r"\bnghiệm thu\b", r"quyết toán dự án", r"\bquyết toán\b",
    r"kiểm toán độc lập", r"\bkiểm toán\b", r"bảo hiểm công trình", r"\bbảo hiểm\b",
    r"thí nghiệm nén tĩnh cọc", r"\bkiểm định\b",
    r"chi thường xuyên", r"kinh phí thường xuyên", r"tài sản công", r"sửa chữa bảo trì",
    r"bộ quốc phòng", r"tt-bqp", r"doanh trại", r"doanh cụ", r"công tác doanh trại",
    r"quân chủng pk-kq", r"công trình quân sự", r"công trình quốc phòng", r"định mức doanh cụ",
    r"quản lý chất lượng", r"phòng cháy chữa cháy", r"\bpccc\b", r"\bqcvn\b", r"\btcvn\b",
    r"quy chuẩn", r"tiêu chuẩn"
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


def cascade_evaluate_document(title: str, summary: str, gatekeeper: LegalGatekeeper) -> Tuple[bool, str, str]:
    """
    Quy trình Lọc 2 Tầng:
    - Tầng 1: Kiểm tra Blacklist & Whitelist Regex (<1ms, 0đ)
    - Tầng 2: Gọi Gemini AI Gatekeeper xác nhận ngữ nghĩa (0.3s)
    """
    combined_text = f"{title} {summary}".lower()

    # 1. Tầng 1A: Kiểm tra Blacklist cứng
    for pattern in HARD_EXCLUDE_PATTERNS:
        if re.search(pattern, combined_text, re.IGNORECASE):
            return False, "TIER_1_BLACKLIST", f"Dính từ khóa cấm: '{pattern}'"

    # 2. Tầng 1B: Kiểm tra Whitelist tiềm năng
    has_domain_keyword = False
    for pattern in DOMAIN_KEYWORDS:
        if re.search(pattern, combined_text, re.IGNORECASE):
            has_domain_keyword = True
            break

    if not has_domain_keyword:
        return False, "TIER_1_NO_KEYWORD", "Không chứa từ khóa chuyên ngành"

    # 3. Tầng 2: Gọi Gemini AI Gatekeeper xác nhận ngữ cảnh thông minh
    triage_res = gatekeeper.triage_document(title, summary)
    if triage_res.get("is_in_scope", False):
        return True, "TIER_2_AI_APPROVED", triage_res.get("reason", "Phù hợp phạm vi dự án")
    else:
        return False, "TIER_2_AI_REJECTED", triage_res.get("reason", "AI gác cổng loại bỏ")


def classify_document_type(title: str) -> Tuple[str, str]:
    title_lower = title.lower()

    if re.search(r"\bluật\b|\bbộ luật\b|nghị quyết.*quốc hội|/qh", title_lower):
        return ("🏛️ LUẬT & NGHỊ QUYẾT QUỐC HỘI", "LUAT")
    
    if re.search(r"\bnghị định\b|/nđ-cp|\bquyết định.*thủ tướng|/qđ-ttg", title_lower):
        return ("📜 NGHỊ ĐỊNH CHÍNH PHỦ", "NGHI_DINH")
    
    if re.search(r"\bthông tư\b|/tt-|/vbhn-", title_lower):
        if "bqp" in title_lower or "quốc phòng" in title_lower:
            return ("🎖️ THÔNG TƯ BỘ QUỐC PHÒNG", "THONG_TU_BQP")
        return ("📑 THÔNG TƯ BỘ NGÀNH (BXD, BKHĐT...)", "THONG_TU")
    
    if re.search(r"\bqcvn\b|\btcvn\b|quy chuẩn|tiêu chuẩn", title_lower):
        return ("📐 QUY CHUẨN & TIÊU CHUẨN KỸ THUẬT", "QUY_CHUAN")

    return ("📌 VĂN BẢN HƯỚNG DẪN & CHỈ ĐẠO", "HUONG_DAN")


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


def format_master_telegram_alert(
    item: dict,
    doc_meta: dict,
    ai_data: dict,
    telegraph_url: str,
    clean_link: str
) -> Tuple[str, dict]:
    """
    Chuẩn hóa giao diện tin nhắn Telegram Master Template:
    - <code> badge cho số hiệu để chạm là copy ngay (Tap-to-Copy)
    - 4 trường sống còn: Hiệu lực, Thay thế, Chuyển tiếp, Gói thầu tác động
    - Top 3 điểm mới định lượng in đậm rõ ràng
    - Inline Keyboard chuẩn 1 Chính + 2 Phụ
    """
    type_label = doc_meta.get("loai_van_ban", "VĂN BẢN QUY PHẠM PHÁP LUẬT")
    doc_title = item.get("title", "")
    source_name = item.get("source_name", "Cơ quan Nhà nước")

    so_hieu_clean = ai_data.get("so_hieu_clean")
    if not so_hieu_clean:
        so_hieu_match = re.search(r"(\d+[\w\/\-\.]+)", doc_title)
        so_hieu_clean = so_hieu_match.group(1) if so_hieu_match else "MỚI"

    ngay_ban_hanh = ai_data.get("ngay_ban_hanh", doc_meta.get("ngay_ban_hanh", "Vừa ban hành"))
    ngay_hieu_luc = ai_data.get("ngay_hieu_luc", ngay_ban_hanh)
    van_ban_thay_the = ai_data.get("van_ban_thay_the", "Chưa có / Văn bản mới")
    chuyen_tiep_ngan = ai_data.get("chuyen_tiep_ngan", "Áp dụng theo quy định hiện hành đối với các gói thầu phát hành trước ngày hiệu lực.")
    
    tags_list = ai_data.get("goi_thau_tags", ["#Đấu_thầu", "#Xây_lắp", "#Tư_vấn"])
    tags_str = " ".join(tags_list)

    # 3 bullets định lượng
    raw_bullets = ai_data.get("summary_top3", ["Đã hoàn thành rà soát và đối chiếu toàn văn."])
    formatted_bullets = []
    for idx, b in enumerate(raw_bullets[:3], 1):
        clean_b = re.sub(r"^\d+[\.\-\)]\s*", "", b).strip()
        formatted_bullets.append(f"{idx}. {clean_b}")
    bullets_text = "\n".join(formatted_bullets)

    message_text = (
        f"🏛 <b>{type_label}</b> | <code>{so_hieu_clean}</code>\n"
        f"────────────────────────\n"
        f"<b>{doc_title}</b>\n"
        f"<i>📅 Ban hành: {ngay_ban_hanh} • 🏢 Cơ quan: {source_name}</i>\n\n"
        f"⏱ <b>HIỆU LỰC & CHUYỂN TIẾP:</b>\n"
        f"• ⚡ <b>Hiệu lực:</b> Từ ngày <code>{ngay_hieu_luc}</code>\n"
        f"• 🔄 <b>Thay thế:</b> <code>{van_ban_thay_the}</code>\n"
        f"• ⚠️ <b>Chuyển tiếp:</b> {chuyen_tiep_ngan}\n"
        f"• 📦 <b>Gói thầu ảnh hưởng:</b> {tags_str}\n\n"
        f"⚖️ <b>3 ĐIỂM THAY ĐỔI CỐT LÕI CẦN ÁP DỤNG:</b>\n"
        f"{bullets_text}"
    )

    inline_keyboard = {
        "inline_keyboard": [
            [
                {"text": "⚡ Đọc Báo Cáo Phân Tích (Instant View)", "url": telegraph_url}
            ],
            [
                {"text": "🌐 Cổng Nguồn", "url": clean_link},
                {"text": "📖 Thư Viện Luật", "url": "https://ditrang6266.github.io/Thu-vien-PL/"}
            ]
        ]
    }

    return message_text, inline_keyboard


def process_and_send_alert(item: dict, ai_analyzer: LegalAIAnalyzer, telegraph_pub: TelegraphPublisher) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        log("ℹ️ Không tìm thấy Token Telegram. Bỏ qua bước gửi tin nhắn.")
        return False

    type_label, type_code = classify_document_type(item["title"])
    clean_link = normalize_url(item["link"])

    pdf_file_path = extract_and_download_pdf(clean_link, item.get("id", "doc"))

    log(f"🧠 [TẦNG 3] Đang gọi AI Gemini phân tích tác động toàn văn cho: {item['title'][:60]}...")
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
        analysis_data=ai_data,
        doc_item=doc_meta
    )

    message_text, reply_markup = format_master_telegram_alert(
        item=item,
        doc_meta=doc_meta,
        ai_data=ai_data,
        telegraph_url=telegraph_url,
        clean_link=clean_link
    )

    sent_success = False
    # 💡 CƠ CHẾ GỘP 1 TIN NHẮN DUY NHẤT: Gửi kèm file PDF nếu có
    if pdf_file_path and os.path.exists(pdf_file_path):
        send_doc_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
        try:
            with open(pdf_file_path, "rb") as f:
                files = {"document": (os.path.basename(pdf_file_path), f, "application/pdf")}
                data = {
                    "chat_id": TELEGRAM_CHAT_ID,
                    "caption": message_text[:1024],
                    "parse_mode": "HTML",
                    "reply_markup": json.dumps(reply_markup)
                }
                res = httpx.post(send_doc_url, data=data, files=files, timeout=40.0)
                if res.status_code == 200:
                    log(f"✅ Đã gửi bản tin Master Template kèm file PDF gốc thành công (1 tin duy nhất): {item['title'][:60]}...")
                    sent_success = True
                else:
                    log(f"⚠️ sendDocument trả về {res.status_code}, chuyển sang sendMessage.")
        except Exception as e:
            log(f"⚠️ Lỗi gửi kèm PDF ({e}), chuyển sang gửi tin nhắn văn bản.")

    # Fallback gửi tin nhắn văn bản nếu không có PDF hoặc upload PDF gặp sự cố
    if not sent_success:
        send_msg_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message_text,
            "parse_mode": "HTML",
            "reply_markup": reply_markup
        }
        try:
            response = httpx.post(send_msg_url, json=payload, timeout=20)
            if response.status_code == 200:
                log(f"✅ Đã gửi thông báo Telegram Master Template thành công: {item['title'][:60]}...")
                sent_success = True
            else:
                log(f"❌ Gửi Telegram thất bại ({response.status_code}): {response.text}")
        except Exception as e:
            log(f"❌ Lỗi kết nối Telegram: {e}")

    # 💡 BƯỚC 2: TỰ ĐỘNG ĐỒNG BỘ VÀO SỔ CÁI EXCEL (Kho_Can_Cu_Phap_Ly.xlsx)
    try:
        type_to_loai = {
            "LUAT": "Luật",
            "NGHI_DINH": "Nghị định",
            "THONG_TU_BQP": "Thông tư",
            "THONG_TU": "Thông tư",
            "QUY_CHUAN": "Quy chuẩn",
            "HUONG_DAN": "Văn bản hướng dẫn"
        }
        type_to_linh_vuc = {
            "LUAT": "Xây dựng & Đấu thầu",
            "NGHI_DINH": "Xây dựng & Đấu thầu",
            "THONG_TU_BQP": "Quốc phòng & Doanh trại",
            "THONG_TU": "Quản lý Chi phí & Dự toán",
            "QUY_CHUAN": "PCCC & Tiêu chuẩn Kỹ thuật",
            "HUONG_DAN": "Chỉ đạo & Điều hành"
        }
        clean_loai = type_to_loai.get(type_code, "Văn bản QPPL")
        clean_linh_vuc = type_to_linh_vuc.get(type_code, "Xây dựng & Quản lý dự án")

        so_hieu_val = ai_data.get("so_hieu_clean")
        if not so_hieu_val or so_hieu_val == "MỚI":
            so_hieu_match = re.search(r"(\d+[\w\/\-\.]+)", item.get("title", ""))
            so_hieu_val = so_hieu_match.group(1) if so_hieu_match else item.get("title", "")[:20]

        sync_payload = {
            "so_hieu_clean": so_hieu_val,
            "van_ban_thay_the": ai_data.get("van_ban_thay_the", ""),
            "title": item.get("title", ""),
            "trich_yeu": item.get("title", ""),
            "linh_vuc": clean_linh_vuc,
            "loai_van_ban": clean_loai,
            "co_quan": item.get("source_name", "Nhà nước"),
            "ngay_ban_hanh": ai_data.get("ngay_ban_hanh", item.get("published", "")),
            "ngay_hieu_luc": ai_data.get("ngay_hieu_luc", ""),
            "chuyen_tiep_ngan": ai_data.get("chuyen_tiep_ngan", ""),
            "goi_thau_tags": ai_data.get("goi_thau_tags", ["ALL"]),
            "telegraph_url": telegraph_url
        }
        excel_file_path = os.path.join(BASE_DIR, "Kho_Can_Cu_Phap_Ly.xlsx")
        sync_legal_document_to_excel(sync_payload, excel_path=excel_file_path)
        log(f"💾 Đã tự động đồng bộ Sổ cái Excel thành công: {excel_file_path}")
    except Exception as e:
        log(f"⚠️ Không thể đồng bộ vào Excel: {e}")

    return sent_success


def run_reconnaissance() -> int:
    init_storage()
    known_docs = load_known_documents()
    new_matched_count = 0

    log("🔍 BẮT ĐẦU CHU TRÌNH TRINH SÁT LỌC ĐA TẦNG (CASCADE FILTERING)...")
    
    gatekeeper = LegalGatekeeper(api_key=GEMINI_API_KEY)
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

                    # ÁP DỤNG QUY TRÌNH LỌC ĐA TẦNG THÔNG MINH
                    is_approved, tier_stage, reason = cascade_evaluate_document(title, summary, gatekeeper)

                    if is_approved:
                        log(f"🎯 [DUYỆT] VĂN BẢN ĐÚNG NGÀNH: {title} (Lý do: {reason})")
                        doc_item = {
                            "id": doc_hash,
                            "title": title,
                            "link": link,
                            "summary": summary,
                            "published": published,
                            "source_name": source["name"],
                            "tier_approved": tier_stage,
                            "discovered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        process_and_send_alert(doc_item, ai_analyzer, telegraph_pub)
                        
                        known_docs[doc_hash] = doc_item
                        new_matched_count += 1
                    else:
                        log(f"🛡️ [LOẠI BỎ] {title[:60]}... -> {tier_stage}: {reason}")
                        known_docs[doc_hash] = {
                            "title": title,
                            "filtered_out": True,
                            "filter_tier": tier_stage,
                            "reject_reason": reason,
                            "discovered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }

                    # Lưu lũy tiến ngay sau mỗi văn bản
                    save_known_documents(known_docs)

            except Exception as e:
                log(f"❌ Lỗi khi quét nguồn {source['name']}: {e}")

    save_known_documents(known_docs)
    log(f"🏁 HOÀN THÀNH CHU TRÌNH TRINH SÁT. Số văn bản được duyệt: {new_matched_count}")
    return new_matched_count


if __name__ == "__main__":
    run_reconnaissance()
