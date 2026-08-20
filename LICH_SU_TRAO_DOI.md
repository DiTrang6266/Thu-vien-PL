# 📜 NHẬT KÝ TRAO ĐỔI VÀ QUYẾT ĐỊNH NGHIỆP VỤ (HANDOVER DIARY)

Tài liệu này ghi lại toàn bộ bối cảnh, các yêu cầu chỉnh đốn của Người dùng, các quyết định nghiệp vụ đã thống nhất và hướng dẫn chuyển giao hệ thống để mở máy khác là nắm được 100%.

---

## 📌 BỐI CẢNH & YÊU CẦU CỦA NGƯỜI DÙNG

### 1. Người Dùng Là Ai?
* Là Giám đốc Ban QLDA / Kỹ sư Lập dự toán / Cán bộ Đấu thầu / Kế toán quản lý tài sản công.
* Cần một hệ thống **Tự động trinh sát 24/7** các văn bản pháp luật mới ban hành, lọc đúng chuyên môn nghiệp vụ thực chiến và đẩy thông báo tức thì về điện thoại qua Telegram kèm bản phân tích sâu và file PDF gốc có dấu mộc đỏ.

### 2. Bốn (04) Trụ Cột Nghiệp Vụ Cốt Lõi Bắt Buộc Theo Dõi:
1. **Quản lý Đầu tư Xây dựng & Quản lý Dự án:** Luật Xây dựng, Luật Đầu tư công, Nghị định 10/2021 (Quản lý chi phí), Nghị định 15/2021 (Quản lý dự án), Nghị định 06/2021 (Quản lý chất lượng, bảo trì), Thông tư 11/2021, Thông tư 12/2021, Định mức xây dựng, Suất vốn đầu tư, Đơn giá nhân công, Giá ca máy, Nghiệm thu thanh quyết toán vốn đầu tư, An toàn lao động thi công.
2. **Đấu thầu & Lựa chọn Nhà thầu:** Luật Đấu thầu số 22/2023/QH15, Nghị định 24/2024/NĐ-CP, Thông tư 06/2024/TT-BKHĐT, Thông tư 07/2024/TT-BKHĐT, các Mẫu E-HSMT, Kế hoạch lựa chọn nhà thầu, Đấu thầu qua mạng VNEPS, Bảo đảm dự thầu, Hợp đồng xây dựng.
3. **Chi Thường xuyên & Mua sắm/Sửa chữa Tài sản Công:** Luật Quản lý, sử dụng tài sản công, Nghị định 151/2017/NĐ-CP, Nghị định 114/2024/NĐ-CP, **Nghị định 138/2024/NĐ-CP** (Sử dụng nguồn kinh phí chi thường xuyên ngân sách nhà nước để mua sắm tài sản, trang thiết bị; cải tạo, nâng cấp, mở rộng, xây dựng mới hạng mục công trình trong các dự án đã đầu tư xây dựng).
4. **Công trình Quốc phòng & An toàn PCCC:** Quy chuẩn QCVN 06 về An toàn cháy cho nhà và công trình, các Thông tư/Quy định của Bộ Quốc phòng về đầu tư xây dựng doanh trại, công trình quân sự.

---

## 🚫 DANH MỤC LOẠI TRỪ DỨT KHOÁT (STRICT BLACKLIST)

Qua các lần trao đổi và chỉ đạo của Người dùng, hệ thống **tuyệt đối gạt bỏ 100% các nhóm sau**:
1. **Quy hoạch không gian đô thị & nông thôn vĩ mô:** Đồ án quy hoạch chung đô thị, quy hoạch phân khu xây dựng, quy hoạch nông thôn mới, cắm mốc giới quy hoạch vùng (thuộc thẩm quyền quản lý vĩ mô của Sở Quy hoạch/UBND, không phục vụ trực tiếp cho việc triển khai dự án, đấu thầu, dự toán hay sửa chữa tài sản công).
2. **Hàng hải & Đường thủy:** Hoa tiêu hàng hải, hoa tiêu đường thủy nội địa, luồng tàu, bến thủy nội địa, đăng kiểm phương tiện thủy, trục vớt cứu hộ, cảng biển.
3. **Giao thông đường bộ & Vận tải:** Sát hạch lái xe, bằng lái, đăng kiểm xe cơ giới, phù hiệu xe, trạm thu phí BOT, vận tải hành khách tuyến cố định, xe buýt, taxi.
4. **Dự thảo & Tuyên truyền:** Các bản tin "Truyền thông dự thảo", "Lấy ý kiến góp ý dự thảo" (chưa ban hành chính thức có hiệu lực).
5. **Văn bản cá biệt & Đặc thù 1 dự án:**
   * Quyết định giao dự toán/kế hoạch vốn cá biệt cho 1 đơn vị/tỉnh (ví dụ: giao vốn cho Ban QLDA 7).
   * Quyết định khen thưởng, bổ nhiệm, điều chuyển xe ô tô cơ quan.
   * Thông tư ban hành định mức đặc thù chỉ dùng riêng cho 1 dự án duy nhất (như Tuyến đường sắt Lào Cai - Hải Phòng, Sân bay Long Thành, Cao tốc riêng...).

---

## 🏗️ CÁC BƯỚC ĐÃ TRIỂN KHAI VÀ HOÀN THIỆN

### 1. Kiến Trúc Phễu 2 Tầng (2-Tier Hybrid Funnel):
* **Tầng 1 - Sàng lọc Thể thức & Loại trừ Ngành ngoài (`classifier_tier2.py`):**
  - Sử dụng Regex và Bộ từ khóa cứng sàng lọc trong **0.06 mili-giây**, chi phí 0đ, 0 token.
  - Chặn đứng 100% rác ngoài ngành, dự thảo và văn bản cá biệt.
* **Tầng 2 - Trích xuất Toàn văn PDF & AI Phân tích Chuyên sâu (`ai_analyzer.py`):**
  - Dùng **PyMuPDF (`fitz`)** tự động đọc toàn văn lên tới 35.000 ký tự từ các trang nội dung kỹ thuật thực chất của file PDF gốc.
  - Gọi Gemini Flash API với bộ chỉ thị **Báo cáo Tham mưu Nghiệp vụ Thực chiến (Executive Impact Report)**:
    + Bóc tách từ 5-8 quy định thực chất từ Điều 3 trở đi kèm mã định danh `[Điều X Khoản Y]`.
    + Bảng đối chiếu Redline Cũ vs Mới.
    + Cảnh báo rủi ro pháp lý & Bẫy kiểm toán/thanh tra.
    + Sinh câu căn cứ Nghị định 30/2020/NĐ-CP để copy 1-chạm dán Word.

### 2. Hệ Thống Xuất Bản & Thông Báo:
* **Telegraph Instant View (`telegraph_publisher.py`):** Tự động tạo bài báo cáo toàn văn trên Telegra.ph, mở tức thì trên điện thoại không tốn thời gian load web.
* **Telegram Bot (`recon_pipeline.py`):**
  - Gửi tin nhắn tóm tắt tinh gọn đọc trong 3 giây.
  - Thẻ `<code>...</code>` chạm 1 cái là copy ngay câu căn cứ Nghị định 30.
  - Đính kèm file PDF gốc có dấu mộc đỏ.
* **Sổ cái Excel Master (`excel_sync_engine.py`):** Tự động chèn dòng mới vào file `Kho_Can_Cu_Phap_Ly.xlsx`.

---

## 🔑 THÔNG TIN XÁC THỰC HỆ THỐNG
* **GitHub Repository:** `https://github.com/DiTrang6266/Thu-vien-PL.git` (Branch `main`)
* **Telegram Bot Token:** `8929996006:AAEkcgtKYRJihNtDZUPxymvAEIDBIlWzqIc`
* **Telegram Chat ID:** `5004771861` (Tên: `lyna`)
* **Gemini API Key:** `AQ.Ab8RN6Ip2cJuK3UlMGyv6iWxuOEoiKyHo1oB61Fbx5b9oLNdqw`
