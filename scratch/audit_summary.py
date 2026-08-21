# -*- coding: utf-8 -*-
import sys, io, openpyxl, json, re
from bs4 import BeautifulSoup

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

wb_kho = openpyxl.load_workbook('Kho_Can_Cu_Phap_Ly.xlsx', data_only=True)
ws_kho = wb_kho.active

wb_book2 = openpyxl.load_workbook('Book2.xlsx', data_only=True)
ws_book2 = wb_book2.active

records = []
for r in range(2, ws_kho.max_row + 1):
    rec = {
        'stt': ws_kho.cell(row=r, column=1).value,
        'linh_vuc': ws_kho.cell(row=r, column=2).value,
        'loai_vb': ws_kho.cell(row=r, column=3).value,
        'so_hieu': str(ws_kho.cell(row=r, column=4).value or '').strip(),
        'trich_yeu': str(ws_kho.cell(row=r, column=5).value or '').strip(),
        'co_quan': str(ws_kho.cell(row=r, column=6).value or '').strip(),
        'ngay_bh': str(ws_kho.cell(row=r, column=7).value or '').strip(),
        'ngay_hl': str(ws_kho.cell(row=r, column=8).value or '').strip(),
        'trang_thai': str(ws_kho.cell(row=r, column=9).value or '').strip(),
        'thay_the': str(ws_kho.cell(row=r, column=10).value or '').strip(),
        'chuyen_tiep': str(ws_kho.cell(row=r, column=11).value or '').strip(),
        'tags': str(ws_kho.cell(row=r, column=12).value or '').strip(),
        'b2_thay_the': str(ws_book2.cell(row=r, column=6).value or '').strip(),
        'b2_chuyen_tiep': str(ws_book2.cell(row=r, column=7).value or '').strip(),
    }
    records.append(rec)

print(f"=== THỐNG KÊ ĐỘ DÀI & ĐẶC TÍNH VĂN BẢN (TỔNG SỐ {len(records)} VĂN BẢN) ===")

trich_yeu_lens = [len(r['trich_yeu']) for r in records]
print(f"Trích yếu: Min={min(trich_yeu_lens)}, Max={max(trich_yeu_lens)}, Avg={sum(trich_yeu_lens)/len(trich_yeu_lens):.1f}")

chuyen_tiep_lens = [len(r['chuyen_tiep']) for r in records]
print(f"Chuyển tiếp: Min={min(chuyen_tiep_lens)}, Max={max(chuyen_tiep_lens)}, Avg={sum(chuyen_tiep_lens)/len(chuyen_tiep_lens):.1f}")

print("\n--- TOP 5 TRÍCH YẾU DÀI NHẤT ---")
sorted_ty = sorted(records, key=lambda x: len(x['trich_yeu']), reverse=True)
for r in sorted_ty[:5]:
    print(f"[{r['stt']}] {r['so_hieu']} ({len(r['trich_yeu'])} ký tự): {r['trich_yeu']}")

print("\n--- TOP 5 TRÍCH YẾU NGẮN NHẤT ---")
for r in sorted_ty[-5:]:
    print(f"[{r['stt']}] {r['so_hieu']} ({len(r['trich_yeu'])} ký tự): {r['trich_yeu']}")

print("\n--- TOP 5 CHUYỂN TIẾP DÀI NHẤT ---")
sorted_ct = sorted(records, key=lambda x: len(x['chuyen_tiep']), reverse=True)
for r in sorted_ct[:5]:
    print(f"[{r['stt']}] {r['so_hieu']} ({len(r['chuyen_tiep'])} ký tự): {r['chuyen_tiep']}")

print("\n--- TOP 5 CHUYỂN TIẾP NGẮN NHẤT ---")
for r in sorted_ct[-5:]:
    print(f"[{r['stt']}] {r['so_hieu']} ({len(r['chuyen_tiep'])} ký tự): {r['chuyen_tiep']}")

# Word grounding sentence inspection
print("\n=== KIỂM TRA CÂU CĂN CỨ WORD GROUNDING ENGINE ===")
sample_clauses = []
for r in records:
    loai_vb = r['loai_vb']
    so_hieu = r['so_hieu']
    co_quan = r['co_quan']
    ngay_bh = r['ngay_bh']
    trich_yeu = r['trich_yeu']
    
    prefix = f"{loai_vb} số {so_hieu}" if loai_vb and not so_hieu.lower().startswith(loai_vb.lower()) else so_hieu
    # Grammar check for connecting word: e.g. "của Quốc hội Luật..." vs "của Quốc hội về..."
    cau = f"Căn cứ {prefix} ngày {ngay_bh} của {co_quan} {trich_yeu};"
    sample_clauses.append((r['stt'], so_hieu, cau, len(cau)))

for stt, sh, c, l in sample_clauses[:10]:
    print(f"[{stt}] ({sh}): {c}")

print("...\nSample cuối:")
for stt, sh, c, l in sample_clauses[-5:]:
    print(f"[{stt}] ({sh}): {c}")
