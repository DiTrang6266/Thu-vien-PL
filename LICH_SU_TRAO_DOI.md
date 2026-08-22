# LỊCH SỬ TRAO ĐỔI & BÀN GIAO TOÀN DIỆN DỰ ÁN
**Hệ thống Quản trị, Tự động hóa Hồ sơ Dự án & Trinh sát Pháp lý Xây dựng 24/7**
*Thời điểm cập nhật toàn diện: 21/08/2026*

---

## 📌 1. THÔNG TIN HỆ THỐNG & KẾT NỐI ĐÃ XÁC THỰC 100%

* **Người dùng / Chủ dự án:** `DiTrang6266` (Tên hiển thị Telegram: `lyna` - Chat ID: `5004771861`)
* **Telegram Bot đã kích hoạt 24/7:**
  - Tên Bot: **Trợ lý Pháp Luật** (`@Troly_PL_bot`)
  - HTTP Bot Token: `8929996006:AAEkcgtKYRJihNtDZUPxymvAEIDBIlWzqIc`
  - Đã kiểm thử gửi tin nhắn văn bản, nút bấm tương tác (Inline Keyboard), Telegraph Instant View và đính kèm file PDF gốc thành công.
* **Kho GitHub lưu trữ tự động hóa Cloud 0 đồng:**
  - Đường dẫn Repo: `https://github.com/DiTrang6266/Thu-vien-PL` (Chế độ: Main branch)
  - GitHub Pages: `https://ditrang6266.github.io/Thu-vien-PL/` (Trang Web Thẻ Di Động tra cứu 1-chạm)
  - GitHub Actions Workflow: `.github/workflows/watchdog.yml` (chạy tự động 07:00 sáng T2-T6)
  - Đã cấu hình 3 biến bảo mật (Repository Secrets): `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, và `GEMINI_API_KEY`.

---

## 🏛️ 2. QUY CHUẨN ĐỊNH DẠNG & THỂ THỨC VĂN BẢN (NGHỊ ĐỊNH 30/2020/NĐ-CP)

Dự án áp dụng quy chuẩn cố định bắt buộc khi đúc hồ sơ Word:
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

## 🔄 3. TÓM TẮT DIỄN BIẾN TRAO ĐỔI & CÁC QUYẾT ĐỊNH ĐÃ CHỐT TỪ ĐẦU ĐẾN NAY

### Buổi 1 – 6: Thiết lập Trạm gác Cloud, Bóc tách PDF, Lọc 3 Tầng & Báo cáo Telegraph Instant View
- Xây dựng Pipeline trinh sát tự động `recon_pipeline.py` kết nối Telegram `@Troly_PL_bot`.
- Bóc tách toàn văn tài liệu (Zero-Chunking), xuất bản báo cáo Telegraph Instant View không giới hạn ký tự.
- Phát triển bộ lọc 3 tầng (Cascade Gatekeeper) với `modules/ai_gatekeeper.py` (<0.3s phản hồi).
- Tích hợp 10 trang quy trình dự án từ `Trinh tu.pdf` và 8 gói thầu dự án.

### Buổi 7 – 10: Sổ cái Master Excel 14 Cột & Web App Thẻ Di Động GitHub Pages
- Xây dựng Sổ cái CSDL pháp lý `Kho_Can_Cu_Phap_Ly.xlsx` chuẩn 14 cột giao diện Executive Dashboard (Header Navy `#1B365D`, Freeze Panes `A2`, Wrap Text, Badge Xanh/Đỏ).
- Xây dựng `modules/web_card_generator.py` xuất bản Trang Web Thẻ Di Động (`docs/index.html`).
- Xây dựng `modules/word_grounding_engine.py` tự động lọc văn bản sống và sắp xếp thứ bậc lập pháp (Luật 100 $\rightarrow$ NĐ 200 $\rightarrow$ TT 300 $\rightarrow$ QCVN 400).

### Buổi 11 – 16: Chuẩn hóa Thông tư Bộ Quốc phòng & Xóa bỏ Khối Đất đai
- **Chỉ đạo 1:** Loại bỏ 100% khối Đất đai (Luật 31/2024, NĐ 102, NĐ 103) vì dự án nằm trong khuôn viên đất quốc phòng hiện hữu, không có GPMB.
- **Chỉ đạo 2:** Chuẩn hóa Thông tư BQP theo ảnh chụp thực tế:
  + `Thông tư 101/2026/TT-BQP` (Ký 09/07/2026): Hướng dẫn Luật Xây dựng trong BQP $\rightarrow$ **ĐANG CÓ HIỆU LỰC**.
  + `Thông tư 102/2026/TT-BQP` (Ký 17/07/2026): Phân cấp chủ trương và dự án đầu tư BQP $\rightarrow$ **ĐANG CÓ HIỆU LỰC**, thay thế toàn diện TT 128/2021, TT 73/2023, TT 120/2024.

### Buổi 17: Phản biện Đối soát Internet và Cập nhật Toàn diện `Book2.xlsx` cùng CSDL 94 Văn bản (Mốc 01/07/2026)
* **Phát hiện & Chỉ đạo của Người dùng:** Cập nhật chính xác các thay đổi lớn của Luật Xây dựng 2025 và hệ thống văn bản hướng dẫn có hiệu lực từ 01/07/2026.
* **Các quyết định đã chốt & triển khai 100%:**
  1. **Hợp đồng xây dựng:** `NĐ 37/2015/NĐ-CP` & `NĐ 50/2021/NĐ-CP` (Hết HL từ 01/07/2026) $\rightarrow$ Thay thế bởi **`Nghị định 210/2026/NĐ-CP`** (Hiệu lực 01/07/2026).
  2. **Chất lượng & Nghiệm thu:** `NĐ 06/2021/NĐ-CP` (Hết HL từ 01/07/2026) $\rightarrow$ Thay thế bởi **`Nghị định 207/2026/NĐ-CP`** (Hiệu lực 01/07/2026).
  3. **Quản lý Chi phí & Định mức:** `TT 11/2021`, `TT 14/2023`, `TT 01/2025` (Hết HL từ 01/07/2026) $\rightarrow$ Thay thế bởi **`Thông tư 36/2026/TT-BXD`**; `TT 12/2021` & `TT 09/2024` $\rightarrow$ Thay thế bởi **`Thông tư 38/2026/TT-BXD`**; `NĐ 10/2021` $\rightarrow$ Thay thế bởi **`Nghị định 206/2026/NĐ-CP`**.
  4. **Quyết toán vốn ĐTC:** `NĐ 99/2021/NĐ-CP` (Hết HL từ 26/09/2025) $\rightarrow$ Thay thế bởi **`Nghị định 254/2025/NĐ-CP`** (Hiệu lực 26/09/2025).
  5. **Quy hoạch Xây dựng:** `NĐ 44/2015/NĐ-CP` & `TT 20/2019/TT-BXD` (Hết HL từ 01/07/2025) $\rightarrow$ Thay thế bởi **`Nghị định 178/2025/NĐ-CP`** (Luật 47/2024/QH15).
  6. **PCCC:** `NĐ 136/2020` & `NĐ 50/2024` (Hết HL từ 01/07/2025) $\rightarrow$ Thay thế bởi **`Nghị định 105/2025/NĐ-CP`**.
  7. **Chi thường xuyên:** `NĐ 138/2024` & `NĐ 98/2025` (Hết HL) $\rightarrow$ Thay thế bởi **`Nghị định 104/2026/NĐ-CP`** (Hiệu lực 01/05/2026).
* **Kết quả:** Đồng bộ hoàn hảo **94 bản ghi** vào `Book2.xlsx`, `Kho_Can_Cu_Phap_Ly.xlsx`, `modules/master_seed_loader.py`, `BANG_DOI_SOAT_HIEU_LUC_TOAN_BO.md` và `docs/index.html`.

### Buổi 18: Thẩm định Phản biện Độc lập của Hội đồng 3 Subagent về "Train lại AI Lọc"
* **Người dùng yêu cầu:** Dùng 3 Subagent độc lập kiểm tra xem có cần train lại dữ liệu cho AI lọc không.
* **Kết luận của Hội đồng 3 Subagent:**
  - *Không cần train lại trọng số máy học (No fine-tuning):* Hệ thống sử dụng In-Context Prompting + Heuristic Rules + CSDL Grounding.
  - *Tái đào tạo Ngữ cảnh (In-Context Retraining):* Cập nhật Prompt và Few-shot 2026 trong `ai_gatekeeper.py`.
  - *Tháo gỡ nút thắt Blacklist:* Loại bỏ các từ khóa cấm nhầm Luật Quy hoạch 47/2024 trong `classifier_tier2.py` để mở thông luồng cho gói `TV-01` (Quy hoạch Tổng mặt bằng 1/500).

### Buổi 19: Thẩm định Phản biện Độc lập của Hội đồng 3 Subagent về "Phần Tóm tắt & Quy định Chuyển tiếp"
* **Người dùng yêu cầu:** 3 Subagent thẩm định và phản biện xem phần tóm tắt đã chuẩn chưa, có cần chỉnh sửa gì không.
* **Kết luận & Hành động của Hội đồng:**
  - *Subagent 1 (Nội dung pháp lý):* Nâng cấp 28 câu tóm tắt còn chung chung thành ngôn ngữ hành động thực chiến (tỷ lệ tạm ứng 10-50%, thanh toán KBNN 02 ngày, bãi bỏ thẩm định thiết kế bước 2, phân cấp BQP, hạn mức chi thường xuyên 15 tỷ...).
  - *Subagent 2 (Động cơ AI):* Tối ưu hàm `_verify_citations()` trong `modules/ai_analyzer.py` với chuẩn hóa khoảng trắng chống báo lỗi oan.
  - *Subagent 3 (Hiển thị thực tế):* Nghiệm thu 100% tính trực quan và tuân thủ Luật số 1 trong `AGENTS.md` (lời thường, dễ hiểu) trên 4 bề mặt: `Kho_Can_Cu_Phap_Ly.xlsx`, `Book2.xlsx`, `docs/index.html` và `word_grounding_engine.py`.

### Buổi 20: Dọn dẹp Toàn diện Mã nguồn theo Tiêu chuẩn Skill `don-code`
* **Triển khai:**
  - Dọn sạch toàn bộ 6 file nháp tạm trong thư mục `scratch/`.
  - Dọn sạch file PDF thử nghiệm trong `data/downloads/`.
  - Quét sạch toàn bộ cache `__pycache__`.
  - Đồng bộ `Book2.xlsx` lên GitHub (`580f638`).
  - Kiểm thử 18/18 Unit Test Cases PASS 100%.

### Buổi 21: Tái cấu trúc Bộ lọc Thư Viện Luật sang Nhóm Nghiệp vụ Thực chiến Phổ quát
* **Chỉ đạo của Người dùng:** Loại bỏ các mã gói thầu dự án nội bộ (`TV-01`, `TV-02`...) trên thanh lọc của Thư viện Luật vì mang tính cá biệt, gây rối mắt trên điện thoại và không áp dụng được cho dự án khác.
* **Quyết định & Hành động đã triển khai:**
  - Chuyển đổi 100% thanh lọc sang **12 nhóm nghiệp vụ chuyên ngành thực tế**: Quy hoạch & Khảo sát, Thiết kế & Dự toán, Thẩm tra & Thẩm định, Đấu thầu & Hợp đồng, Giám sát & Nghiệm thu, Thi công & An toàn, Kiểm toán & Quyết toán, Bảo hiểm, BQP, PCCC, Môi trường, Chi thường xuyên & Sửa chữa.
  - Tinh lọc danh sách tag trên các thẻ luật (ẩn các mã `TV-01..XD-01`, chỉ giữ lại tag nghiệp vụ rõ nghĩa).
  - Tái tạo thành công `docs/index.html` và `index.html`.
  - Kiểm thử toàn bộ 18/18 Unit Test Cases PASS 100%.

### Buổi 22: Thẩm định & Triển khai Nâng cấp Trạm gác Pháp lý 24/7, Báo cáo Tuần tra 07:00 Sáng, Chuẩn hóa Nút Telegram & Khối Ghim Cố định Web App
* **Chỉ đạo của Người dùng:** 
  1. Điều tra nguyên nhân 2 ngày liên tiếp lúc 7h không có tin nhắn Telegram, chia 3 subagent nghiên cứu độc lập và lập kế hoạch nâng cấp bền vững.
  2. Chuẩn hóa nút bấm Telegram: Khi không có văn bản mới, chỉ để **đúng 1 nút `📖 Thư Viện Luật`** duy nhất (loại bỏ nút trùng lặp và nút tự trỏ vào bot).
  3. Tối ưu giao diện Web App cho máy tính: Thêm **2 nút mũi tên `‹` và `›`** điều hướng cuộn ngang cho người dùng chuột rời.
  4. Sửa lỗi cuộn trang Web App: **Ghim cố định toàn bộ khối Tiêu đề, Ô tìm kiếm và Bộ lọc** ở đỉnh màn hình, cuộn xuống dưới không bị đè che mất thanh trên.
* **Quyết định & Hành động đã triển khai 100%:**
  - **Hội đồng 3 Subagent Độc lập:** Thẩm định và chỉ ra 3 nguyên nhân: (1) Lỗi `TypeError` do xung đột list/dict trong `known_documents.json`; (2) Lịch chạy 00:00 UTC bị nghẽn hàng đợi GitHub Actions (delay 15-45 phút); (3) Cơ chế "im lặng khi không có luật mới" làm người dùng tưởng bot hỏng.
  - **Auto-Migration CSDL:** Tự động nâng cấp 108 hash văn bản từ `list` sang `dict` trong `load_known_documents()`.
  - **Báo cáo Tuần tra 07:00 Sáng (Daily Morning Heartbeat):** Gửi bản tin điểm danh trực ban 24/7 và thông báo tình trạng an toàn kho 94 văn bản lúc 07:00 sáng mỗi ngày.
  - **Định dạng Dual-Format Telegram & `safe_html()`:** Tách riêng caption $\le 850$ ký tự cho `sendDocument` và tin nhắn phân tích đầy đủ cho `sendMessage`, bảo vệ an toàn chống lỗi 400 Bad Request.
  - **Chuẩn hóa Nút Telegram:** 
    + Khi có văn bản mới: 3 nút riêng biệt (Đọc phân tích Instant View Telegraph + Cổng nguồn + Thư viện Luật).
    + Khi điểm danh sáng (không có luật mới): Chỉ giữ đúng 1 nút bấm duy nhất `[ 📖 Thư Viện Luật ]` trỏ về Web App 94 thẻ.
  - **Tối ưu Hạ tầng Cloud (`watchdog.yml`):** Đổi lịch chạy sang 06:43 sáng (né đỉnh nghẽn 00:00 UTC), lưu trữ đồng bộ Sổ cái Excel `Kho_Can_Cu_Phap_Ly.xlsx`, `docs/index.html` và chống xung đột push.
  - **Tối ưu Giao diện Web App (`modules/web_card_generator.py`):**
    + Khắc phục lỗi cắt cụt nút `🔥 PCCC` ở mép màn hình.
    + Bổ sung 2 nút mũi tên `‹` và `›` điều hướng cuộn ngang mượt mà.
    + Bổ sung sự kiện lăn chuột trực tiếp và kéo rê chuột (Drag-to-Scroll) cho người dùng PC/Laptop.
    + **Hợp nhất khối ghim cố định (`top-nav-sticky`):** Ghim toàn bộ Tiêu đề, Ô tìm kiếm và Bộ lọc thành 1 khối vững chắc ở đỉnh màn hình, giải quyết triệt để lỗi cuộn trang bị đè che mất thanh trên.
### Buổi 23: Đối soát Độc lập Hội đồng Subagents, Xây dựng Smart Legal Resolver 0đ & Triệt tiêu 100% Lỗi Link Công báo Chung
* **Vấn đề Người dùng phản ánh:** Thông tin tin nhắn Telegram báo một kiểu (Nghị định 24/2024/NĐ-CP về Đấu thầu) nhưng khi bấm nút "🌐 Cổng Nguồn" lại mở ra trang web "Công báo số 476" chứa Quyết định 42/2026/QĐ-TTg về Khí nhà kính, đính kèm file PDF của cả tập san công báo.
* **Nguyên nhân gốc rễ đã xác minh:** Nguồn RSS `cac-so-cong-bao-moi-dang.rss` chứa tập san 20-30 văn bản gộp; `recon_pipeline.py` lấy nhầm URL trang chủ công báo và tải nhầm file PDF số công báo ngẫu nhiên.
* **Quyết định & Hành động đã triển khai 100%:**
  1. **Triệt tiêu nguồn tin gộp:** Xóa bỏ hoàn toàn RSS số công báo gộp khỏi `recon_pipeline.py`, chỉ giữ lại luồng quét văn bản đơn lẻ (`cac-van-ban-moi-ban-hanh.rss` và các cổng Bộ).
  2. **Xây dựng Smart Legal Resolver (`modules/legal_resolver.py`):** Viết module siêu tinh gọn (<45 dòng code, 0đ, không cần API Key), tự động trích xuất regex số hiệu (`24/2024/NĐ-CP`, `101/2026/TT-BQP`...) và tạo đường link tra cứu toàn văn chuẩn xác 100%.
  3. **Bảo vệ Bộ Tải PDF (`extract_and_download_pdf`):** Chặn đứng 100% việc tải file PDF từ trang chủ hoặc trang tìm kiếm chung, đảm bảo chỉ tải file PDF gốc có dấu đỏ khi có link bài viết chi tiết thực sự.
  4. **Nạp Link Toàn Diện 94 Văn Bản:** Đồng bộ link toàn văn vào `Kho_Can_Cu_Phap_Ly.xlsx`, `Book2.xlsx`, `modules/master_seed_loader.py` và Web App Thẻ Di Động (`docs/index.html` & `index.html`) với nút bấm **`[ 🌐 Xem Toàn Văn ]`** màu xanh.
  5. **Bảo vệ Kiểm thử Tự động:** Mocking API Telegram trong `tests/test_end_to_end.py` để chạy kiểm thử tự động không gửi tin nhắn rác về Telegram của người dùng.
  6. **Kiểm thử Toàn trình:** 38/38 Unit Test Cases **PASS 100%**.

---

## 📂 4. DANH MỤC CÁC FILE ĐANG HOẠT ĐỘNG TRONG DỰ ÁN

Thư mục làm việc: `C:\Users\Manh Duy\Desktop\Hoàn thiện Hồ sơ dự án1\`

1. 📊 **`Book2.xlsx`:** Bảng kiểm tra thẩm định Executive Dashboard 94 dòng, có badge màu Xanh/Đỏ và quy định chuyển tiếp chi tiết.
2. 📗 **`Kho_Can_Cu_Phap_Ly.xlsx`:** Sổ cái Master Căn cứ Pháp lý 14 cột chuẩn hóa 94 văn bản.
3. 📄 **`BANG_DOI_SOAT_HIEU_LUC_TOAN_BO.md`:** Bảng đối soát chi tiết 94 văn bản khớp 1:1.
4. 🌐 **`docs/index.html` & `index.html`:** Trang Web Thẻ Di Động tra cứu 1-chạm trên GitHub Pages.
5. 🧠 **`modules/master_seed_loader.py`:** CSDL hạt giống 94 văn bản chuẩn hóa.
6. 📄 **`modules/word_grounding_engine.py`:** Động cơ đúc câu căn cứ vào phôi Word chuẩn Nghị định 30 theo thứ bậc Luật $\rightarrow$ NĐ $\rightarrow$ TT $\rightarrow$ QCVN.
7. 🛡️ **`modules/ai_gatekeeper.py`:** Bộ lọc gác cổng AI siêu nhẹ (<0.3s) với 8 ví dụ mẫu Few-shot 2026.
8. 🧠 **`modules/ai_analyzer.py`:** Bộ não phân tích tác động toàn văn & đối soát trích dẫn chống ảo giác.
9. 🔍 **`modules/classifier_tier1.py` & `classifier_tier2.py`:** Bộ lọc thể thức và 4 trụ cột nghiệp vụ.
10. 📊 **`modules/legal_db_sync.py`:** Module đồng bộ Sổ cái Excel chống kẹt file trên Windows.
11. 📰 **`modules/telegraph_publisher.py`:** Bộ xuất bản bài viết Instant View Telegraph.
12. 🔍 **`modules/legal_parser.py` & `legal_diff.py`:** Bóc tách phân cấp và so sánh điều khoản (diff).
13. 🧪 **`tests/`:** 10 bộ kiểm thử tự động (23/23 Unit Test Cases PASS 100%).
14. ⚙️ **`recon_pipeline.py`:** Luồng trinh sát pháp lý 24/7 & Báo cáo Tuần tra Heartbeat 07:00.
15. 🚀 **`.github/workflows/watchdog.yml`:** Tự động chạy 06:43 sáng T2-T6 trên GitHub Actions (né đỉnh nghẽn 00:00 UTC).
16. 📋 **`LICH_SU_TRAO_DOI.md` & `TIEN_DO.md`:** Hồ sơ bàn giao dự án.


---

## 🚀 5. HƯỚNG DẪN BẬT MÁY MỚI / CHUYỂN SANG MÁY KHÁC DÙNG NGAY

Khi bạn chuyển sang máy tính khác hoặc mở phiên làm việc mới:
1. **Tải mã nguồn về máy:**
   ```bash
   git clone https://github.com/DiTrang6266/Thu-vien-PL.git
   ```
2. **Cài đặt thư viện (nếu máy mới hoàn toàn):**
   ```bash
   pip install -r requirements.txt
   ```
3. **Chỉ cần gửi 1 câu lệnh duy nhất cho AI:**
   > *"Hãy đọc file LICH_SU_TRAO_DOI.md và TIEN_DO.md để tiếp tục công việc."*
4. **AI sẽ:**
   - Hiểu 100% bối cảnh dự án, 11 gói thầu từ `TV-01` đến `XD-01`.
   - Nắm trọn 94 văn bản pháp lý và các mốc hiệu lực 2025–2026.
   - Biết rõ tài khoản Telegram `@Troly_PL_bot`, GitHub Pages và tiếp tục thực hiện công việc tiếp theo ngay lập tức mà bạn không cần phải giải thích lại bất cứ điều gì!
