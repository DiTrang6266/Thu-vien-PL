# -*- coding: utf-8 -*-
"""
Unit test kiểm thử module ai_analyzer.
"""

import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.ai_analyzer import LegalAIAnalyzer


def test_ai_analyzer_structure():
    analyzer = LegalAIAnalyzer()

    sample_old = "Điều 15. Hồ sơ mời thầu bao gồm thông tin chi tiết về gói thầu."
    sample_new = "Điều 15. Hồ sơ mời thầu bao gồm thông tin chi tiết về gói thầu và yêu cầu bảo lãnh số."

    res = analyzer.analyze_legal_impact(sample_old, sample_new)
    print("AI Analysis Output Structure Keys:", list(res.keys()))

    assert "summary_top3" in res
    assert "impact_areas" in res
    assert "transition_rules" in res
    assert "verification_summary" in res

    # Kiểm tra phương thức verify_citations
    fake_ai_output = {
        "detailed_articles_diff": [
            {
                "article_id": "Điều 15",
                "exact_quote_old": "Hồ sơ mời thầu bao gồm thông tin chi tiết về gói thầu",
                "exact_quote_new": "Hồ sơ mời thầu bao gồm thông tin chi tiết về gói thầu và yêu cầu bảo lãnh số"
            },
            {
                "article_id": "Điều 99",
                "exact_quote_old": "Câu trích dẫn ảo giác không có thật",
                "exact_quote_new": "Câu trích dẫn ảo giác không có thật"
            }
        ]
    }

    verified_res = analyzer._verify_citations(fake_ai_output, sample_old, sample_new)
    diff_items = verified_res["detailed_articles_diff"]

    assert diff_items[0]["is_verified"] is True
    assert diff_items[1]["is_verified"] is False
    assert verified_res["verification_summary"]["verified_exact_items"] == 1
    assert verified_res["verification_summary"]["total_items"] == 2

    print(f"Verified items count: {verified_res['verification_summary']['verified_exact_items']}/{verified_res['verification_summary']['total_items']}")
    print("[OK] Test AI Analyzer & Strict Verifier passed successfully!")


if __name__ == "__main__":
    test_ai_analyzer_structure()
