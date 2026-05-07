import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from netkeiba.breeding import _is_excluded_year, _build_progeny_result


def test_is_excluded_year_recent():
    assert _is_excluded_year("2024105929", 2026) is True


def test_is_excluded_year_current():
    assert _is_excluded_year("2026100001", 2026) is True


def test_is_excluded_year_older():
    assert _is_excluded_year("2023105286", 2026) is False


def test_is_excluded_year_much_older():
    assert _is_excluded_year("2019104926", 2026) is False


def test_is_excluded_year_boundary():
    # 2023 < 2024 なので除外しない
    assert _is_excluded_year("2023999999", 2026) is False


def test_build_progeny_result_full():
    info = {
        "name": "テスト馬",
        "sex": "牡",
        "prize_money": "1000万円",
        "prize_money_nra": "0万円",
        "career_record": "5戦2勝 [2-1-0-2]",
        "notable_wins": ["共同通信杯"],
    }
    result = _build_progeny_result("2023105286", info)
    assert result == {
        "name": "テスト馬",
        "horse_id": "2023105286",
        "prize_money": "1000万円",
        "prize_money_nra": "0万円",
        "career_record": "5戦2勝 [2-1-0-2]",
        "notable_wins": ["共同通信杯"],
    }


def test_build_progeny_result_missing_fields():
    info = {"name": "テスト馬"}
    result = _build_progeny_result("2023105286", info)
    assert result["name"] == "テスト馬"
    assert result["horse_id"] == "2023105286"
    assert result["prize_money"] is None
    assert result["prize_money_nra"] is None
    assert result["career_record"] is None
    assert result["notable_wins"] is None
