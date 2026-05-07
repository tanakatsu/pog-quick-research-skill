import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from netkeiba.horse_info import _parse_sex


def test_parse_sex_with_status_prefix():
    # 現役ステータスが先頭に来るフォーマット (例: デビュー前・現役馬)
    assert _parse_sex("現役　牡2歳　黒鹿毛") == "牡"


def test_parse_sex_female_with_status_prefix():
    assert _parse_sex("現役　牝3歳　鹿毛") == "牝"


def test_parse_sex_gelding_with_status_prefix():
    assert _parse_sex("現役　セン5歳　栗毛") == "セン"


def test_parse_sex_without_status_prefix():
    # ステータスなしの旧フォーマット
    assert _parse_sex("牡　栗毛") == "牡"


def test_parse_sex_none_input():
    assert _parse_sex(None) is None


def test_parse_sex_no_sex_token():
    assert _parse_sex("黒鹿毛") is None
