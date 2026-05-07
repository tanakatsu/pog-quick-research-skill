import asyncio
import re
import sys
from datetime import date

from playwright.async_api import BrowserContext

from netkeiba.horse_info import fetch_horse_info
from netkeiba.retry import with_retry

_HORSE_ID_RE = re.compile(r"/horse/(?:ped/)?([0-9a-z]+)/?")


def _is_excluded_year(horse_id: str, current_year: int) -> bool:
    """馬IDの先頭4桁が current_year-2 以降なら除外対象（True）を返す。"""
    return horse_id[:4] >= str(current_year - 2)


def _build_progeny_result(horse_id: str, info: dict) -> dict:
    """fetch_horse_info() の返り値から産駒の成績フィールドを抽出して返す。"""
    return {
        "name": info.get("name"),
        "horse_id": horse_id,
        "prize_money": info.get("prize_money"),
        "prize_money_nra": info.get("prize_money_nra"),
        "career_record": info.get("career_record"),
        "notable_wins": info.get("notable_wins"),
    }
