# 🏛️ HỆ THỐNG TRẠM GÁC & TRINH SÁT PHÁP LUẬT TỰ ĐỘNG 24/7

Hệ thống AI tự động giám sát, sàng lọc 4 trụ cột nghiệp vụ thực chiến (Đầu tư công/Xây dựng, Đấu thầu, Chi thường xuyên/Sửa chữa tài sản công, Quốc phòng/PCCC), tóm tắt chuyên sâu chống ảo giác và gửi thông báo Telegram kèm PDF gốc.

---

## 🚀 HƯỚNG DẪN CHẠY TRÊN MÁY TÍNH MỚI (CHỈ CẦN 3 BƯỚC)

### Bước 1: Tải mã nguồn về máy
```bash
git clone https://github.com/DiTrang6266/Thu-vien-PL.git
cd Thu-vien-PL
```

### Bước 2: Cài đặt các thư viện cần thiết
```bash
pip install httpx feedparser beautifulsoup4 pymupdf openpyxl pytest
```

### Bước 3: Chạy thử nghiệm và kiểm tra hệ thống
* **Chạy bộ kiểm thử tự động (8 ca kiểm thử):**
  ```bash
  pytest tests/test_all_pipelines.py -v
  ```
* **Chạy trinh sát và gửi thông báo live về Telegram:**
  ```bash
  python recon_pipeline.py
  ```

---

## 📁 CẤU TRÚC THƯ MỤC CHÍNH
* `recon_pipeline.py`: File điều phối luồng trinh sát toàn trình.
* `modules/classifier_tier1.py`: Bóc tách số hiệu, thẩm quyền cơ quan, ngày ban hành chuẩn NĐ 30.
* `modules/classifier_tier2.py`: Bộ lọc gác cổng 4 trụ cột thực chiến & danh mục loại trừ ngoài ngành.
* `modules/ai_analyzer.py`: Động cơ AI Gemini đọc hiểu toàn văn PDF và lập Báo cáo Tham mưu Chuyên sâu.
* `modules/telegraph_publisher.py`: Xuất bản bài báo cáo Instant View lên nền tảng Telegra.ph.
* `modules/excel_sync_engine.py`: Tự động đồng bộ Sổ cái pháp lý Excel Master.
* `LICH_SU_TRAO_DOI.md`: Nhật ký chi tiết toàn bộ các quyết định nghiệp vụ và yêu cầu của người dùng.
* `TIEN_DO.md`: Báo cáo tiến độ và trạng thái sẵn sàng của hệ thống.
