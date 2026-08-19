@echo off
chcp 65001 >nul
title TỰ ĐỘNG HÓA XUẤT HỒ SƠ DỰ ÁN 1-CHẠM
color 1F

echo =====================================================================
echo    HỆ THỐNG QUẢN TRỊ VÀ XUẤT HỒ SƠ DỰ ÁN XÂY DỰNG 1-CHẠM (OFFLINE)
echo    Quy chuẩn Thể thức: Nghị định số 30/2020/NĐ-CP
echo =====================================================================
echo.
echo [*] Đang đọc dữ liệu từ Excel và đúc trọn bộ file Word...
echo.

set PYTHONIOENCODING=utf-8
python "%~dp0xuat_ho_so_1cham.py"

echo.
echo =====================================================================
echo [*] Đang mở thư mục kết quả để bạn kiểm tra...
echo =====================================================================
explorer.exe "%~dp0KET_QUA_XUAT_HO_SO"

pause
