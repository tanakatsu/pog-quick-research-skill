import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.filter_comments import parse_date, comment_date, filter_comments
from datetime import date

COMMENTS = [
    {"no": 1, "date": "2023/12/29 21:51", "text": "A"},
    {"no": 2, "date": "2024/6/1 10:00", "text": "B"},
    {"no": 3, "date": "2024/12/31 23:59", "text": "C"},
    {"no": 4, "date": "2025/5/31 12:35", "text": "D"},
    {"no": 5, "date": "2025/6/1 0:00", "text": "E"},
]


def test_parse_date():
    assert parse_date("20240101") == date(2024, 1, 1)
    assert parse_date("20251231") == date(2025, 12, 31)


def test_comment_date():
    assert comment_date({"date": "2024/6/1 10:00"}) == date(2024, 6, 1)
    assert comment_date({"date": "2023/12/29 21:51"}) == date(2023, 12, 29)


def test_filter_to_only():
    result = filter_comments(COMMENTS, from_date=None, to_date=date(2025, 5, 31))
    assert [c["no"] for c in result] == [1, 2, 3, 4]


def test_filter_from_only():
    result = filter_comments(COMMENTS, from_date=date(2024, 6, 1), to_date=None)
    assert [c["no"] for c in result] == [2, 3, 4, 5]


def test_filter_both():
    result = filter_comments(COMMENTS, from_date=date(2024, 1, 1), to_date=date(2024, 12, 31))
    assert [c["no"] for c in result] == [2, 3]


def test_filter_none():
    result = filter_comments(COMMENTS, from_date=None, to_date=None)
    assert result == COMMENTS


def test_filter_inclusive_endpoints():
    result = filter_comments(COMMENTS, from_date=date(2023, 12, 29), to_date=date(2023, 12, 29))
    assert [c["no"] for c in result] == [1]
