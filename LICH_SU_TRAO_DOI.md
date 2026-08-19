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
  - GitHub Actions Workflow: `.github/workflows/watchdog.yml`
  - Đã cấu hình 2 biến bảo mật (Repository Secrets): `TELEGRAM_BOT_TOKEN` và `TELEGRAM_CHAT_ID`.

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

---

## 📂 4. DANH MỤC CÁC FILE ĐÃ HOÀN THIỆN TRONG THƯ MỤC DỰ ÁN

Thư mục làm việc chính: `C:\Users\Manh Duy\Desktop\Hoàn thiện Hồ sơ dự án\`

1. 📡 **`recon_pipeline.py`:** Kịch bản trinh sát pháp luật tự động đọc RSS, lọc từ khóa, tải PDF và gửi Telegram.
2. ⚙️ **`.github/workflows/watchdog.yml`:** Kịch bản hẹn giờ tự động chạy 07:00 sáng trên GitHub Actions.
3. 📊 **`Kho_Can_Cu_Phap_Ly.xlsx`:** Sổ cái pháp lý 15 văn bản sống cốt lõi ngành xây dựng.
4. 📋 **`Du_lieu_mau_du_an.xlsx`:** Bảng điều khiển dự án 4 sheet (`Chan_doan_quy_trinh`, `Thong_tin_chung`, `Danh_muc_goi_thau`, `Bang_du_toan`).
5. 🚀 **`xuat_ho_so_1cham.py`:** Động cơ đọc Excel và đúc trọn bộ file Word cho từng gói thầu.
6. ⚡ **`CHAY_TU_DONG.bat`:** File 1-click click đúp chuột trên Desktop để xuất hồ sơ.
7. 📄 **`Template_01_To_trinh_mau.docx`:** Phôi Word Tờ trình số 01 chuẩn thể thức 13pt/14pt.
8. 📑 **`01` $\rightarrow$ `08` biểu mẫu Markdown:** Bộ mẫu Tờ trình, Báo cáo thẩm định, Thư mời thầu, Quyết định...

---

## 🚀 5. HƯỚNG DẪN KHI BẬT MÁY MỚI HOẶC BẮT ĐẦU PHIÊN MỚI

Khi bạn chuyển sang máy tính mới hoặc mở lại phiên làm việc:
1. Mở file này (`LICH_SU_TRAO_DOI.md`) và file `TIEN_DO.md` để xem lại toàn bộ bối cảnh.
2. Kiểm tra Python đã cài các thư viện: `pip install docxtpl openpyxl httpx feedparser beautifulsoup4`.
3. Chỉ cần nói với AI: *"Hãy tiếp tục thực hiện theo file LICH_SU_TRAO_DOI.md"* là AI sẽ nắm trọn toàn bộ dự án ngay lập tức mà không cần hỏi lại từ đầu!
