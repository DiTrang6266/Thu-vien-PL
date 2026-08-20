# LỊCH SỬ TRAO ĐỔI & BÀN GIAO TOÀN DIỆN DỰ ÁN
**Hệ thống Quản trị, Tự động hóa Hồ sơ Dự án & Trinh sát Pháp lý Xây dựng 24/7**

---

## 📌 1. THÔNG TIN CHUNG VÀ TÀI KHOẢN HỆ THỐNG ĐÃ XÁC THỰC 100%

* **Người dùng / Chủ dự án:** `DiTrang6266` (Tên hiển thị Telegram: `lyna` - Chat ID: `5004771861`)
* **Telegram Bot đã kích hoạt:**
  - Tên Bot: **Trợ lý Pháp Luật** (`@Troly_PL_bot`)
  - HTTP Bot Token: `8929996006:AAEkcgtKYRJihNtDZUPxymvAEIDBIlWzqIc`
  - Đã kiểm thử gửi tin nhắn văn bản, nút bấm tương tác (Inline Keyboard) và đính kèm file PDF gốc thành công.
* **Kho GitHub lưu trữ tự động hóa Cloud 0 đồng:**
  - Đường dẫn Repo: `https://github.com/DiTrang6266/Thu-vien-PL` (Chế độ: Private)
  - GitHub Actions Workflow: `.github/workflows/watchdog.yml` (chạy tự động 07:00 sáng T2-T6)
  - Đã cấu hình 3 biến bảo mật (Repository Secrets): `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, và `GEMINI_API_KEY`.
  - Đã tích hợp Personal Access Token (PAT) để máy tính tự động đồng bộ và quản trị kho trực tiếp bằng dòng lệnh 100%.

---

## 🏛️ 2. QUY CHUẨN ĐỊNH DẠNG & THỂ THỨC VĂN BẢN (NGHỊ ĐỊNH 30/2020/NĐ-CP)

Dự án áp dụng quy chuẩn cố định bắt buộc, không thay đổi:
* **CỐ ĐỊNH 13.0 pt:**
  - Mục 1: Cơ quan chủ quản (Times New Roman 13pt)
  - Mục 2: Cơ quan ban hành (Times New Roman 13pt, ĐẬM)
  - Mục 3: Quốc hiệu "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM" (Times New Roman 13pt, ĐẬM)
  - Mục 4: Tiêu ngữ "Độc lập - Tự do - Hạnh phúc" (Times New Roman 13pt, ĐẬM, gạch chân)
  - Mục 5: Số ký hiệu (Times New Roman 13pt)
  - Mục 6: Địa danh, ngày tháng năm (Times New Roman 13pt, NGHIÊNG)
  - Mục 14: Số trang Header căn giữa từ trang thứ 2 (Times New Roman 13pt)
* **CỐ ĐỊNH 14.0 pt:**
  - Mục 7: Tên loại văn bản (TỜ TRÌNH, QUYẾT ĐỊNH...) (Times New Roman 14pt, ĐẬM)
  - Mục 8: Trích yếu nội dung (Times New Roman 14pt, ĐẬM)
  - Mục 9: Nơi nhận / Kính gửi (Times New Roman 14pt)
  - Mục 10: Toàn bộ nội dung chính (Times New Roman 14pt, Căn đều Justify, Thụt lề dòng đầu 1.27cm, Giãn đoạn 6pt)
  - Mục 11: Chức vụ người ký (Times New Roman 14pt, ĐẬM)
  - Mục 12: Họ và tên người ký (Times New Roman 14pt, ĐẬM)
* **Quy chuẩn Căn lề trang:** Trái: 30 mm, Phải: 15 mm, Trên: 20 mm, Dưới: 20 mm.

---

## 🔄 3. TÓM TẮT DIỄN BIẾN TRAO ĐỔI & CÁC QUYẾT ĐỊNH ĐÃ CHỐT

### Buổi 1: Xây dựng Cỗ máy Trinh sát Pháp lý & Kết nối Telegram
* **Vấn đề đặt ra:** Cập nhật văn bản pháp luật ngành Xây dựng / Đấu thầu tự động hoàn toàn MIỄN PHÍ và không cần treo máy tính 24/7.
* **Quyết định chốt:** Dùng mô hình lai "Cloud 0 đồng + Local Offline":
  - **Cloud:** Dùng GitHub Actions chạy định kỳ 07:00 sáng mỗi ngày từ T2 - T6 để quét RSS Công báo và Cổng Bộ Xây dựng (`recon_pipeline.py`).
  - **Thông báo:** Đẩy tức thì về Telegram cá nhân của người dùng.
* **Kết quả:** Đã bắn thành công các bản tin và file PDF gốc về Telegram của người dùng.

### Buổi 2: Sửa lỗi Link, Bóc tách File PDF gốc và Xóa bỏ rác thông tin
* **Phát hiện của người dùng:** Link trên tin nhắn bị lệch nội dung so với bài báo, và tin tức báo chí chung chung không có giá trị áp dụng hồ sơ.
* **Quyết định chốt:**
  1. Phân định rạch ròi 2 tầng: **Loại bỏ 100% tin tức báo chí, tin điều hành chung, tin lễ tết**. Chỉ theo dõi **Văn bản QPPL chính thức** (Luật, Nghị định, Thông tư, Quy chuẩn QCVN, Định mức dự toán).
  2. Bắt buộc có bằng chứng đối soát: **Gửi đính kèm trực tiếp file PDF gốc (.pdf) có dấu mộc đỏ/chữ ký số** vào Telegram qua `sendDocument`.
  3. Đã xử lý triệt để lỗi `Referer Header` chống chặn tải file của Cổng Chính phủ (`datafiles.chinhphu.vn`), gửi thành công file PDF 1MB mở mượt trên Foxit PhantomPDF.

### Buổi 3: Nghiên cứu Kiến trúc "NotebookLM Tự Động Hóa 100%" (Zero-Touch Grounded AI)
* **Ý tưởng của người dùng:** Dùng cơ chế như NotebookLM để AI tự động đọc văn bản sửa đổi, chỉ ra điểm thay đổi cốt lõi liên quan đến mình mà không cần mở file đọc từng dòng.
* **Quyết định chốt:** Xây dựng Pipeline tự động 4 bước:
  - *Bước 1:* Crawler tự động tải file PDF văn bản mới.
  - *Bước 2:* Tự động lấy file PDF văn bản cũ bị sửa đổi từ kho dữ liệu.
  - *Bước 3:* Đẩy cả 2 file PDF vào Gemini API (Source-Grounded AI) để bóc tách:
    + Top 3 thay đổi cốt lõi ảnh hưởng hồ sơ dự án.
    + Bảng so sánh 3 cột: `[Điều khoản]` - `[Quy định cũ]` - `[Quy định mới]`.
    + Điều khoản chuyển tiếp cho các hồ sơ đang làm dở.
    + Trích dẫn nguyên văn số trang và số Điều, Khoản (Zero-Hallucination).
  - *Bước 4:* Tự động gửi file PDF + Bản tin đối chiếu vào Telegram và cập nhật Sổ cái Excel.

### Buổi 4: Đột phá Giải pháp Tự động hóa 100% & Báo cáo Toàn văn Không Giới Hạn (Telegraph Instant View)
* **Kết quả nghiên cứu của 3 Subagent:**
  1. *Subagent 1 (Full-Document Context):* Loại bỏ RAG cắt vụn. Áp dụng **Full-Document (Zero-Chunking)** với Context Window 1M–2M token của Gemini Flash/Pro.
  2. *Subagent 2 (Legal Diff & Redline):* Bóc tách phân cấp Điều/Khoản kết hợp so khớp từng từ ngữ (`python-redlines` / `diff-match-patch`) sinh Redline Track Changes và đối soát trích dẫn gốc 100%.
  3. *Subagent 3 (Telegraph Instant View):* Dùng **Telegraph API** tạo báo cáo Instant View tức thì không giới hạn ký tự.
* **Triển khai Trọn bộ 4 Module:** `modules/legal_parser.py`, `modules/legal_diff.py`, `modules/ai_analyzer.py`, `modules/telegraph_publisher.py`.

### Buổi 5: Tối ưu Toàn diện Gemini AI, Bóc tách File Trình tự & Chuẩn Hóa Phân Loại
* **Các quyết định đã triển khai:**
  1. **Dynamic Model Discovery:** `modules/ai_analyzer.py` tự động truy vấn danh sách model Gemini khả dụng nhất (Gemini 3.7 Flash, 3.1 Pro, 2.5 Flash...), triệt tiêu lỗi 404/503.
  2. **Bao quát 100% file `Trinh tu.pdf`:** Nạp trọn vẹn 8 gói thầu dự án (TV-04, TV-05, TV-06, TV-07, TV-08, TV-09, PTV-01, XD-01).
  3. **Lọc từ khóa Đấu thầu qua mạng & Văn bản BQP:** Tích hợp `muasamcong`, `e-hsmt`, `e-hsdt`, `e-tbmt`, Thông tư BQP 36/2023, 150/2018, 69/2026, 101/2026.
  4. **Chuẩn hóa Phân loại Tin nhắn Telegram thành 4 Nhóm theo Luật Ban hành VBQPPL:**
     - 🏛️ **LUẬT & NGHỊ QUYẾT QUỐC HỘI**
     - 📜 **NGHỊ ĐỊNH & QUYẾT ĐỊNH CHÍNH PHỦ / THỦ TƯỚNG**
     - 📑 **THÔNG TƯ CÁC BỘ & 🎖️ THÔNG TƯ BỘ QUỐC PHÒNG**
     - 📌 **VĂN BẢN HƯỚNG DẪN, CÔNG VĂN & QUY CHUẨN KỸ THUẬT (QCVN/TCVN)**

### Buổi 6: Dọn dẹp & Tinh gọn Kho GitHub, Kích hoạt Tự động hóa qua Personal Access Token (PAT)
* **Yêu cầu của người dùng:** Xóa sạch toàn bộ các file không liên quan đến Trạm gác cổng Internet trên GitHub (phôi Word, file dữ liệu dự án nội bộ).
* **Kết quả thực hiện:**
  1. Đã cấu hình xác thực GitHub qua Personal Access Token (`ghp_...`).
  2. Đã gỡ bỏ toàn bộ 30 file mẫu hồ sơ nội bộ khỏi Git và cập nhật `.gitignore` chuẩn.
  3. Đã đẩy lệnh xóa lên mạng thành công 100%: Kho `Thu-vien-PL` trên GitHub hiện tại chỉ chứa DUY NHẤT bộ máy Gác cổng 24/7 (`recon_pipeline.py`, `.github/workflows/`, `modules/`, `data/`, `requirements.txt`).

---

## 📂 4. DANH MỤC CÁC FILE ĐANG ĐƯỢC QUẢN TRỊ TRÊN GITHUB

Kho lưu trữ: `https://github.com/DiTrang6266/Thu-vien-PL`

1. 📡 **`recon_pipeline.py`:** Kịch bản trinh sát tự động toàn trình (Crawler 5 Cổng Quốc gia + AI Gemini + Telegraph Instant View + Tải PDF gốc + Bắn Telegram).
2. ⚙️ **`.github/workflows/watchdog.yml`:** Kịch bản hẹn giờ chạy 07:00 sáng trên GitHub Actions.
3. 🧠 **`modules/ai_analyzer.py`:** Bộ não AI phân tích tác động toàn văn + Tự động khám phá model Gemini + Kiểm tra trích dẫn 100%.
4. ⚖️ **`modules/legal_diff.py`:** Bộ đối chiếu từng từ ngữ (Redline) và lớp kiểm tra trích dẫn gốc chống ảo giác.
5. 🔍 **`modules/legal_parser.py`:** Bộ bóc tách cấu trúc Chương $ightarrow$ Điều $ightarrow$ Khoản $ightarrow$ Điểm kèm số trang PDF.
6. 📰 **`modules/telegraph_publisher.py`:** Bộ xuất bản báo cáo Instant View không giới hạn ký tự trên Telegraph.
7. 📦 **`requirements.txt`:** Danh sách thư viện cần thiết.
8. 📁 **`data/`:** Cơ sở dữ liệu ghi nhớ văn bản đã quét (`known_documents.json`) và nhật ký hệ thống.
9. 🧪 **`test_live_ai.py` & `tests/`:** Bộ script kiểm thử phân tích AI thực tế và kiểm thử tích hợp.
10. 📜 **`LICH_SU_TRAO_DOI.md` & `TIEN_DO.md`:** Nhật ký và tiến độ toàn diện của dự án.
