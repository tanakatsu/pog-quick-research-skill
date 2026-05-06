import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from netkeiba.board import _parse_comment_page

SAMPLE = """\
 [1227] No.1さん FJApFxM フォローする

この馬菊花賞向きそう！

2026/4/30 22:28

5

非表示・報告

 [1226] ぺんたさん IZaFCSI フォローする

POG指名馬。馬主ほどは損してないとおさめよう。

2026/4/30 18:14

0

非表示・報告
"""


def test_parse_single_comment():
    text = """\
 [1227] No.1さん FJApFxM フォローする

この馬菊花賞向きそう！

2026/4/30 22:28

5

非表示・報告
"""
    result = _parse_comment_page(text)
    assert result == [{"no": 1227, "date": "2026/4/30 22:28", "text": "この馬菊花賞向きそう！"}]


def test_parse_multiple_comments():
    result = _parse_comment_page(SAMPLE)
    assert len(result) == 2
    assert result[0] == {"no": 1227, "date": "2026/4/30 22:28", "text": "この馬菊花賞向きそう！"}
    assert result[1] == {"no": 1226, "date": "2026/4/30 18:14", "text": "POG指名馬。馬主ほどは損してないとおさめよう。"}


def test_parse_empty_text():
    assert _parse_comment_page("") == []
