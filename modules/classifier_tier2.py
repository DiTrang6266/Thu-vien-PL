# -*- coding: utf-8 -*-
"""
Module: classifier_tier2.py
Mục đích: Lớp 2 trong Phễu phân loại lai (3-Tier Hybrid Funnel) - Sàng lọc Thể thức & Chuyên môn siêu tốc (< 0.1ms).
4 TRỤ CỘT THỰC CHIẾN BẮT BUỘC:
1. DAU_TU_CONG_XAY_DUNG: Quản lý dự án, chi phí đầu tư, định mức, dự toán, suất vốn đầu tư, quản lý chất lượng, nghiệm thu thanh quyết toán công trình.
2. DAU_THAU_MUA_SAM: Luật Đấu thầu, E-HSMT, E-HSDT, kế hoạch LCNT, lựa chọn nhà thầu, hợp đồng xây dựng.
3. CHI_THUONG_XUYEN_TSCONG: Quản lý sử dụng tài sản công, nguồn vốn sự nghiệp/chi thường xuyên sửa chữa, cải tạo, bảo dưỡng, mua sắm tài sản công (NĐ 138/2024, NĐ 114/2024, NĐ 151/2017).
4. QUOC_PHONG_PCCC: Công trình quốc phòng, doanh trại quân đội, an toàn PCCC công trình (QCVN 06).

LOẠI TRỪ DỨT KHOÁT (STRICT BLACKLIST):
- Quy hoạch không gian đô thị, quy hoạch nông thôn, đồ án quy hoạch xã/vùng (vĩ mô của Sở Quy hoạch/UBND).
- Hàng hải, đường thủy, hoa tiêu, cảng biển, đăng kiểm tàu bè, luồng tàu.
- Vận tải đường bộ, đăng kiểm xe, bằng lái, sát hạch lái xe, trạm thu phí.
- Dự thảo đang lấy ý kiến, truyền thông dự thảo, tin bài tuyên truyền.
- Quyết định cá biệt (phê duyệt dự án riêng, giao vốn cho 1 đơn vị, khen thưởng, bổ nhiệm).
"""

import re
import logging
from enum import Enum
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class DomainEnum(str, Enum):
    DAU_TU_CONG_XAY_DUNG = "DAU_TU_CONG_XAY_DUNG"
    DAU_THAU_MUA_SAM = "DAU_THAU_MUA_SAM"
    CHI_THUONG_XUYEN_TSCONG = "CHI_THUONG_XUYEN_TSCONG"
    QUOC_PHONG_PCCC = "QUOC_PHONG_PCCC"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"


class HybridTier2Classifier:
    STRICT_OUT_OF_SCOPE_BLACKLIST = [
        # 1. Mảng Quy hoạch không gian đô thị & Nông thôn vĩ mô
        "quy hoạch đô thị và nông thôn", "quy hoạch đô thị", "quy hoạch nông thôn", "đồ án quy hoạch chung",
        "nhiệm vụ quy hoạch", "quy hoạch phân khu đô thị", "quy hoạch nông thôn mới", "quy hoạch phân khu xây dựng",
        "cắm mốc giới quy hoạch", "quy hoạch xây dựng vùng", "quy hoạch phân vùng", "quy hoạch mạng lưới",
        
        # 2. Mảng Dự thảo đang lấy ý kiến (Chưa ban hành chính thức)
        "truyền thông dự thảo", "lấy ý kiến dự thảo", "dự thảo thông tư", "dự thảo nghị định",
        "góp ý dự thảo", "dự thảo quyết định", "truyền thông chính sách",
        
        # 3. Hàng hải & Đường thủy nội địa
        "hoa tiêu", "luồng hàng hải", "bến thủy nội địa", "khu neo đậu", "cảng biển",
        "trục vớt cứu hộ", "đăng kiểm tàu", "phương tiện thủy nội địa", "thuyền viên",
        "bằng thuyền trưởng", "bằng máy trưởng", "hoa tiêu hàng hải", "hoa tiêu đường thủy",
        "nạo vét vùng nước", "cảng thủy nội địa", "bến thủy",
        
        # 4. Giao thông đường bộ & Vận tải hành khách
        "sát hạch lái xe", "giấy phép lái xe", "bằng lái xe", "đăng kiểm xe cơ giới",
        "phù hiệu xe", "trạm thu phí bot", "tải trọng trục xe", "vận tải hành khách",
        "xe buýt", "taxi", "niên hạn sử dụng xe", "vận tải đường bộ", "hoạt động bay", "an ninh hàng không",
        "vận tải hàng không", "đường sắt thời kỳ",
        
        # 5. Ngành ngoài khác (Y tế, Giáo dục, Nông nghiệp, Thuế TNCN...)
        "bảo vệ thực vật", "thú y", "tiêm phòng", "trồng rừng", "cấp bù giá thủy lợi",
        "giống cây trồng", "giống vật nuôi", "kiểm dịch động vật",
        "thuốc bảo hiểm y tế", "phác đồ điều trị", "khám chữa bệnh", "hành nghề y",
        "chương trình giáo dục", "chuẩn đầu ra", "học phí", "sách giáo khoa",
        "thuế thu nhập cá nhân", "bảo hiểm thất nghiệp", "lương tối thiểu", "thai sản",
        "hộ tịch", "chứng thực", "trợ cấp xã hội", "thi hành án", "tố tụng"
    ]

    REJECT_INDIVIDUAL_PATTERNS = [
        r"(?:phê duyệt|chấp thuận)\s+(?:chủ trương đầu tư|dự án|báo cáo NCKT|kế hoạch lựa chọn nhà thầu|kết quả lựa chọn nhà thầu|thiết kế bản vẽ|dự toán).+?(?:tại|thuộc|của|tỉnh|huyện|thành phố|ban quản lý|công ty|tổng công ty)",
        r"(?:giao|điều chỉnh|bổ sung|phân bổ|kéo dài thời gian thực hiện)\s+(?:kế hoạch vốn|dự toán|dự toán chi|dự toán ngân sách|chi tiết vốn|ngân sách).*?(?:cho|năm 20\d\d|đợt \d+)",
        r"(?:bổ nhiệm|miễn nhiệm|điều động|luân chuyển|khen thưởng|kỷ luật|cử đi công tác|nghỉ hưu|thành lập hội đồng|thành lập ban chỉ đạo)",
        r"(?:thu hồi đất|giao đất|cho thuê đất|chuyển mục đích sử dụng đất).+?(?:để thực hiện dự án|cho công ty|tại xã|tại phường)",
        r"(?:xếp hạng doanh nghiệp|công nhận kết quả|chỉ định đơn vị|ủy quyền thực hiện|điều chuyển xe ô tô|điều chuyển tài sản)",
        r"(?:v/v|về việc)\s+(?:giao|phân bổ|điều chỉnh)\s+(?:dự toán|kế hoạch vốn|ngân sách).+?cho"
    ]

    PROJECT_SPECIFIC_PATTERNS = [
        r"dự án thành phần \d+",
        r"tuyến đường sắt lào cai\s*-\s*hà nội\s*-\s*hải phòng",
        r"sân bay long thành",
        r"cảng hàng không quốc tế long thành",
        r"đường bộ cao tốc bắc\s*-\s*nam",
        r"tuyến metro số \d+",
        r"đường sắt đô thị tuyến số \d+",
        r"cầu vượt sông \w+",
        r"nhà máy nhiệt điện \w+",
        r"nhà máy thủy điện \w+",
        r"khu tái định cư \w+",
        r"đường trường sơn đông"
    ]

    DOMAIN_ANCHORS = {
        DomainEnum.DAU_TU_CONG_XAY_DUNG: [
            "đầu tư công", "luật xây dựng", "quản lý dự án", "quản lý dự án đầu tư", "chi phí đầu tư xây dựng",
            "dự toán xây dựng", "định mức xây dựng", "định mức dự toán", "tổng mức đầu tư", "chủ trương đầu tư",
            "quy chuẩn kỹ thuật quốc gia", "qcvn", "tiêu chuẩn quốc gia", "tcvn", "thẩm định thiết kế",
            "nghiệm thu công trình", "quản lý chất lượng công trình", "bảo trì công trình", "phân cấp công trình",
            "hợp đồng xây dựng", "giám sát thi công", "khảo sát xây dựng", "chỉ số giá xây dựng",
            "suất vốn đầu tư", "giá ca máy", "đơn giá nhân công xây dựng", "thanh quyết toán vốn đầu tư",
            "an toàn lao động trong thi công", "kiểm định kỹ thuật an toàn", "cốp pha", "máy thi công", "máy ép cọc"
        ],
        DomainEnum.DAU_THAU_MUA_SAM: [
            "đấu thầu", "luật đấu thầu", "lựa chọn nhà thầu", "hồ sơ mời thầu", "e-hsmt", "e-hsyc",
            "hồ sơ dự thầu", "e-hsdt", "kế hoạch lựa chọn nhà thầu", "khlcnt", "đấu thầu qua mạng",
            "mạng đấu thầu quốc gia", "vneps", "chỉ định thầu", "chào hàng cạnh tranh", "bảo đảm dự thầu",
            "bảo lãnh tạm ứng", "hợp đồng trọn gói", "hợp đồng theo đơn giá", "tổ chuyên gia", "tổ thẩm định"
        ],
        DomainEnum.CHI_THUONG_XUYEN_TSCONG: [
            "tài sản công", "quản lý tài sản công", "luật quản lý, sử dụng tài sản công",
            "chi thường xuyên", "kinh phí chi thường xuyên", "vốn sự nghiệp",
            "sửa chữa tài sản công", "bảo dưỡng tài sản công", "cải tạo công trình",
            "nâng cấp công trình", "mua sắm tài sản công", "mua sắm tập trung",
            "tiêu chuẩn định mức máy móc", "tiêu chuẩn định mức xe ô tô", "thuê tài sản công",
            "thanh lý tài sản công", "tiêu chuẩn định mức sử dụng trụ sở", "nghị định 138/2024", "nghị định 114/2024"
        ],
        DomainEnum.QUOC_PHONG_PCCC: [
            "quốc phòng", "công trình quốc phòng", "doanh trại", "doanh trại quân đội",
            "bộ quốc phòng", "quân khu", "công trình chiến đấu", "khu quân sự",
            "pccc", "phòng cháy", "chữa cháy", "an toàn cháy", "qcvn 06", "thẩm duyệt pccc", "nghiệm thu pccc",
            "giải pháp kỹ thuật nâng cao an toàn phòng cháy"
        ]
    }

    def classify_and_filter(
        self,
        title: str,
        content_preview: str = "",
        doc_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        combined_text = f"{title} {content_preview}".lower()

        # 1. Chặn Blacklist dứt khoát
        for black_word in self.STRICT_OUT_OF_SCOPE_BLACKLIST:
            if re.search(r"\b" + re.escape(black_word) + r"\b", combined_text, re.IGNORECASE):
                return {
                    "is_accepted": False,
                    "target_domain": DomainEnum.OUT_OF_SCOPE,
                    "decision": "DROP_OUT_OF_SCOPE_INDUSTRY",
                    "reason": f"Thuộc danh mục loại trừ: {black_word}."
                }

        # 2. Chặn Văn bản cá biệt / Quyết định riêng
        for pattern in self.REJECT_INDIVIDUAL_PATTERNS:
            if re.search(pattern, title, re.IGNORECASE):
                return {
                    "is_accepted": False,
                    "target_domain": DomainEnum.OUT_OF_SCOPE,
                    "decision": "DROP_INDIVIDUAL_DECISION",
                    "reason": "Quyết định cá biệt / giao vốn riêng / phê duyệt dự án cụ thể."
                }

        # 3. Chặn Văn bản đặc thù 1 dự án riêng
        for p_pattern in self.PROJECT_SPECIFIC_PATTERNS:
            if re.search(p_pattern, title, re.IGNORECASE):
                return {
                    "is_accepted": False,
                    "target_domain": DomainEnum.OUT_OF_SCOPE,
                    "decision": "DROP_PROJECT_SPECIFIC_DOC",
                    "reason": "Văn bản định mức/quy chế đặc thù cho 1 dự án cá biệt."
                }

        # 4. Tính điểm 4 Trụ cột Chuyên môn Cốt lõi
        domain_scores = {
            DomainEnum.DAU_TU_CONG_XAY_DUNG: 0,
            DomainEnum.DAU_THAU_MUA_SAM: 0,
            DomainEnum.CHI_THUONG_XUYEN_TSCONG: 0,
            DomainEnum.QUOC_PHONG_PCCC: 0
        }

        for domain, keywords in self.DOMAIN_ANCHORS.items():
            for kw in keywords:
                if kw in combined_text:
                    domain_scores[domain] += 1

        best_domain = max(domain_scores, key=domain_scores.get)
        max_score = domain_scores[best_domain]

        if max_score > 0:
            return {
                "is_accepted": True,
                "target_domain": best_domain,
                "decision": "ROUTE_TO_TIER3_AI_GATEKEEPER",
                "match_score": max_score,
                "reason": f"Phù hợp trụ cột nghiệp vụ thực chiến: {best_domain}."
            }

        return {
            "is_accepted": False,
            "target_domain": DomainEnum.OUT_OF_SCOPE,
            "decision": "DROP_NO_DOMAIN_MATCH",
            "reason": "Không thuộc 4 Trụ cột Nghiệp vụ Thực chiến (Đầu tư công/Xây dựng, Đấu thầu, Chi thường xuyên/Tài sản công, Quốc phòng/PCCC)."
        }
