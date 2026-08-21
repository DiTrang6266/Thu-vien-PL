# -*- coding: utf-8 -*-
import sys, io, openpyxl, json, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

wb_kho = openpyxl.load_workbook('Kho_Can_Cu_Phap_Ly.xlsx', data_only=True)
ws_kho = wb_kho.active

wb_book2 = openpyxl.load_workbook('Book2.xlsx', data_only=True)
ws_book2 = wb_book2.active

# Let's inspect by category
categories = {}
for r in range(2, ws_kho.max_row + 1):
    linh_vuc = str(ws_kho.cell(row=r, column=2).value or '').strip()
    so_hieu = str(ws_kho.cell(row=r, column=4).value or '').strip()
    trich_yeu = str(ws_kho.cell(row=r, column=5).value or '').strip()
    trang_thai = str(ws_kho.cell(row=r, column=9).value or '').strip()
    thay_the = str(ws_kho.cell(row=r, column=10).value or '').strip()
    chuyen_tiep = str(ws_kho.cell(row=r, column=11).value or '').strip()
    tags = str(ws_kho.cell(row=r, column=12).value or '').strip()

    b2_thay_the = str(ws_book2.cell(row=r, column=6).value or '').strip()
    b2_chuyen_tiep = str(ws_book2.cell(row=r, column=7).value or '').strip()

    if linh_vuc not in categories:
        categories[linh_vuc] = []
    categories[linh_vuc].append({
        'stt': r - 1,
        'so_hieu': so_hieu,
        'trich_yeu': trich_yeu,
        'trang_thai': trang_thai,
        'thay_the': thay_the,
        'chuyen_tiep': chuyen_tiep,
        'tags': tags,
        'b2_thay_the': b2_thay_the,
        'b2_chuyen_tiep': b2_chuyen_tiep
    })

print(f"Tổng số lĩnh vực: {len(categories)}")
for cat, items in categories.items():
    print(f"\n📁 Lĩnh vực: {cat} ({len(items)} văn bản)")
    for it in items:
        print(f"  - [{it['stt']}] {it['so_hieu']} ({it['trang_thai']}):")
        print(f"      Trích yếu: {it['trich_yeu']}")
        print(f"      Chuyển tiếp/Điểm mới: {it['chuyen_tiep']}")
        if it['thay_the']:
            print(f"      Thay thế: {it['thay_the']}")
