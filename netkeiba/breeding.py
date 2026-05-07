import asyncio
import re
import sys
from datetime import date

from playwright.async_api import BrowserContext

from netkeiba.horse_info import fetch_horse_info
from netkeiba.retry import with_retry

_HORSE_ID_RE = re.compile(r"/horse/(?:ped/)?(\d[0-9a-z]+)/?")


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


async def fetch_breeding_performance(
    context: BrowserContext,
    mare_id: str,
    concurrency: int = 5,
) -> dict:
    """母馬ページから産駒一覧を取得し、各産駒の競走成績を並列フェッチして返す。

    Returns:
        {
            "mare_name": str,
            "progeny_results": [
                {
                    "name": str | None,
                    "horse_id": str,
                    "prize_money": str | None,
                    "prize_money_nra": str | None,
                    "career_record": str | None,
                    "notable_wins": list[str] | None,
                }
            ]
        }
    """
    page = await context.new_page()
    try:
        await _load_page(page, f"https://db.netkeiba.com/horse/mare/{mare_id}")

        mare_name = (await page.locator("h1").nth(1).inner_text()).strip()

        current_year = date.today().year
        progeny_ids: list[str] = []
        seen: set[str] = set()

        try:
            await page.locator("table.race_table_01").wait_for(timeout=15000)
            links = page.locator("table.race_table_01 a[href*='/horse/']")
            count = await links.count()
            for i in range(count):
                href = await links.nth(i).get_attribute("href") or ""
                m = _HORSE_ID_RE.search(href)
                if not m:
                    continue
                horse_id = m.group(1)
                if horse_id in seen:
                    continue
                seen.add(horse_id)
                if not _is_excluded_year(horse_id, current_year):
                    progeny_ids.append(horse_id)
        except Exception as e:
            print(f"[warn] 産駒リスト取得失敗: {e}", file=sys.stderr)
    finally:
        await page.close()

    sem = asyncio.Semaphore(concurrency)

    async def fetch_one(horse_id: str) -> dict | None:
        async with sem:
            try:
                info = await fetch_horse_info(context, horse_id)
                return _build_progeny_result(horse_id, info)
            except Exception as e:
                print(
                    f"[warn] 産駒 {horse_id} の取得失敗（スキップ）: {e}",
                    file=sys.stderr,
                )
                return None

    results = await asyncio.gather(*[fetch_one(hid) for hid in progeny_ids])
    progeny_results = [r for r in results if r is not None]

    return {
        "mare_name": mare_name,
        "progeny_results": progeny_results,
    }


@with_retry(max_attempts=3, base_delay=1.0)
async def _load_page(page, url: str) -> None:
    await page.goto(url)
    await page.wait_for_load_state("domcontentloaded")
