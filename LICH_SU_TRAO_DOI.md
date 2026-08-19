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
  - *Bước 3:* Đẩy cả 2 file PDF vào Gemini API (Source-Grounded AI) để bóc tách.
  - *Bước 4:* Tự động gửi file PDF + Bản tin đối chiếu vào Telegram và cập nhật Sổ cái Excel.

### Buổi 4: Đột phá Giải pháp Tự động hóa 100% & Báo cáo Toàn văn Không Giới Hạn (Telegraph Instant View)
* **Người dùng yêu cầu:** Phân chia Subagent nghiên cứu các phương án khả thi hơn từ mã nguồn mở và mạng xã hội, đảm bảo tự động 100%, không bị tóm tắt cắt gọt làm mất ý nghĩa pháp lý.
* **Kết quả nghiên cứu của 3 Subagent:**
  1. *Subagent 1 (Parsing & Long Context):* Loại bỏ RAG cắt vụn (Chunking). Áp dụng **Full-Document (Zero-Chunking)** với cửa sổ ngữ cảnh 1M–2M token của Gemini Flash/Pro để AI nhìn thấy trọn vẹn toàn bộ văn bản.
  2. *Subagent 2 (Legal Diff & Redline):* Áp dụng thuật toán bóc tách phân cấp Điều/Khoản (`Docling` / `PyMuPDF`) kết hợp so khớp từng từ ngữ (`python-redlines` / `diff-match-patch`) để sinh chuỗi Redline Track Changes và lớp kiểm tra trích dẫn gốc chống ảo giác 100%.
  3. *Subagent 3 (Kiến trúc & Phân phối Toàn văn):* Dùng **Telegraph API** tạo báo cáo Instant View tức thì không giới hạn ký tự (vượt qua mốc 4.096 ký tự của Telegram), chi phí 0đ trên GitHub Actions.
* **Triển khai Trọn bộ 4 Việc:**
  - **Việc 1:** Hoàn thành `modules/legal_parser.py` và `modules/legal_diff.py`.
  - **Việc 2:** Hoàn thành `modules/ai_analyzer.py` tích hợp Gemini Pro/Flash và lớp hậu kiểm đối soát trích dẫn gốc chống ảo giác.
  - **Việc 3:** Hoàn thành `modules/telegraph_publisher.py` tự động xuất bản bài viết Instant View.
  - **Việc 4:** Hoàn thành nâng cấp `recon_pipeline.py`, `.github/workflows/watchdog.yml` và chạy kiểm thử toàn trình `tests/test_end_to_end.py` thành công 100%, đã bắn bản tin kèm Instant View trực tiếp vào Telegram của người dùng.

### Buổi 5: Tối ưu Gemini 3.7/3.1, Bóc tách File Trình tự & Chuẩn hóa Phân loại Pháp lý
* **Người dùng phản hồi & Yêu cầu:**
  1. Yêu cầu AI không được nói chung chung, phải phân tích thực tế sâu sắc (số ngày, tỷ lệ %, hạn mức tiền, điều khoản chuyển tiếp).
  2. Yêu cầu cập nhật phiên bản Gemini AI mới nhất trên Google AI Studio.
  3. Yêu cầu kiểm tra bao quát toàn bộ 10 trang của file `Trinh tu.pdf` trong folder dự án và nguồn kinh phí chi thường xuyên.
  4. Yêu cầu loại bỏ từ khóa thừa và nạp đầy đủ từ khóa chuyên sâu về **Đấu thầu qua mạng**.
  5. Yêu cầu gom chuẩn phân loại tin nhắn theo đúng thứ bậc văn bản pháp luật của Nhà nước.
* **Các quyết định đã triển khai và chốt 100%:**
  1. **Nâng cấp Gemini AI:** `modules/ai_analyzer.py` ưu tiên tự động gọi **Gemini 3.7 Flash** (mô hình mới nhất tháng 8/2026 chuyên suy luận logic và bóc tách tài liệu) và **Gemini 3.1 Pro**.
  2. **Dữ liệu thật & Link sống 100%:** Khắc phục lỗi 404, liên kết trực tiếp bài viết chính thức của Nghị định 24/2024/NĐ-CP trên Cơ sở dữ liệu Pháp luật và tự động tải đính kèm file PDF gốc có dấu mộc đỏ vào Telegram.
  3. **Bao quát 100% file `Trinh tu.pdf`:** Nạp trọn vẹn 8 gói thầu dự án (TV-04 Lập thiết kế BVTC-DT, TV-05 Thẩm tra thiết kế, TV-06 Lập HSYC & ĐG HSĐX, TV-07 Thí nghiệm nén tĩnh cọc, TV-09 Kiểm toán độc lập, PTV-01 Bảo hiểm công trình, XD-01 Thi công & Doanh cụ, TV-08 Tư vấn giám sát).
  4. **Lọc từ khóa & Tích hợp Đấu thầu qua mạng:**
     - *Đã loại bỏ:* `cục công trình quốc phòng`, `thông tư 65/2021`, `thông tư 68/2022`, `nghị định 138/2024`, `phụ lục 03a/PL03A`.
     - *Đã nạp sâu:* `đấu thầu qua mạng`, `mạng đấu thầu quốc gia`, `muasamcong`, `e-hsmt`, `e-hsdt`, `e-tbmt`, `e-hsyc`, `e-hsdx`, `bảo lãnh dự thầu điện tử`, `mở thầu qua mạng`, `làm rõ e-hsdt`, `thông tư 06/2024`, `thông tư 07/2024`...
     - *Tích hợp văn bản BQP:* Thông tư 36/2023/TT-BQP (Điều lệ Doanh trại), Thông tư 150/2018/TT-BQP & 69/2026/TT-BQP (Định mức Doanh cụ, trang thiết bị), Thông tư 101/2026/TT-BQP.
  5. **Chuẩn hóa Phân loại Tin nhắn Telegram thành 4 Nhóm theo Luật Ban hành VBQPPL:**
     - 🏛️ **LUẬT & NGHỊ QUYẾT QUỐC HỘI**
     - 📜 **NGHỊ ĐỊNH & QUYẾT ĐỊNH CHÍNH PHỦ / THỦ TƯỚNG**
     - 📑 **THÔNG TƯ CÁC BỘ & 🎖️ THÔNG TƯ BỘ QUỐC PHÒNG**
     - 📌 **VĂN BẢN HƯỚNG DẪN, CÔNG VĂN & QUY CHUẨN KỸ THUẬT (QCVN/TCVN)**
  6. **Đồng bộ mã nguồn:** Toàn bộ code mới nhất đã được đẩy lên kho GitHub `DiTrang6266/Thu-vien-PL` (mã commit `980e8c3`).

---

## 📂 4. DANH MỤC CÁC FILE ĐÃ HOÀN THIỆN TRONG THƯ MỤC DỰ ÁN

Thư mục làm việc chính: `C:\Users\Admin\Desktop\Hoàn thiện Hồ sơ dự án\`

1. 📡 **`recon_pipeline.py`:** Kịch bản trinh sát tự động toàn trình (Crawler 5 Cổng Quốc gia + AI Gemini 3.7/3.1 + Telegraph Instant View + Tải PDF gốc + Bắn Telegram).
2. ⚙️ **`.github/workflows/watchdog.yml`:** Kịch bản hẹn giờ chạy 07:00 sáng trên GitHub Actions.
3. 📊 **`Kho_Can_Cu_Phap_Ly.xlsx`:** Sổ cái pháp lý 15 văn bản nền tảng ngành xây dựng & đấu thầu.
4. 📋 **`Du_lieu_mau_du_an.xlsx`:** Bảng điều khiển dự án 4 sheet (`Chan_doan_quy_trinh`, `Thong_tin_chung`, `Danh_muc_goi_thau`, `Bang_du_toan`).
5. 🚀 **`xuat_ho_so_1cham.py`:** Động cơ đọc Excel và đúc trọn bộ file Word cho từng gói thầu.
6. ⚡ **`CHAY_TU_DONG.bat`:** File 1-click click đúp chuột trên Desktop để xuất hồ sơ.
7. 📄 **`Template_01_To_trinh_mau.docx`:** Phôi Word Tờ trình số 01 chuẩn thể thức 13pt/14pt.
8. 📑 **`01` $\rightarrow$ `08` biểu mẫu Markdown:** Bộ mẫu Tờ trình, Báo cáo thẩm định, Thư mời thầu, Quyết định...
9. 🔍 **`modules/legal_parser.py`:** Bộ bóc tách cấu trúc Chương $\rightarrow$ Điều $\rightarrow$ Khoản $\rightarrow$ Điểm kèm số trang PDF.
10. ⚖️ **`modules/legal_diff.py`:** Bộ đối chiếu từng từ ngữ (Redline) và lớp kiểm tra trích dẫn gốc chống ảo giác.
11. 🧠 **`modules/ai_analyzer.py`:** Bộ não AI phân tích tác động toàn văn (Gemini 3.7 Flash & 3.1 Pro) + Kiểm tra trích dẫn 100%.
12. 📰 **`modules/telegraph_publisher.py`:** Bộ xuất bản báo cáo Instant View không giới hạn ký tự trên Telegraph.
13. 📑 **`Trinh tu.pdf`:** File gốc quy định trình tự 8 gói thầu dự án Trường CĐKT PK-KQ.
14. 🧪 **`test_live_ai.py` & `tests/`:** Bộ script kiểm thử phân tích AI thực tế và kiểm thử tích hợp.

---

## 🚀 5. HƯỚNG DẪN KHI BẬT MÁY MỚI HOẶC BẮT ĐẦU PHIÊN MỚI

Khi bạn chuyển sang máy tính mới hoặc mở lại phiên làm việc:
1. Clone hoặc mở thư mục repo: `https://github.com/DiTrang6266/Thu-vien-PL`.
2. Mở file này (`LICH_SU_TRAO_DOI.md`) và file `TIEN_DO.md` để nắm toàn bộ bối cảnh và các quyết định đã chốt.
3. Cài đặt các thư viện cần thiết: `pip install -r requirements.txt`.
4. Chỉ cần nói với AI: *"Hãy tiếp tục thực hiện theo file LICH_SU_TRAO_DOI.md"* là AI sẽ hiểu 100% toàn bộ hệ thống ngay lập tức mà bạn không cần phải giải thích lại một lời nào!
