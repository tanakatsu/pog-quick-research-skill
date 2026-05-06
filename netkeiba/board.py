import asyncio
import re
import sys
from pathlib import Path

from playwright.async_api import BrowserContext

from netkeiba.retry import with_retry


async def fetch_all_board_comments(
    context: BrowserContext,
    horse_id: str,
    output_dir: Path,
    concurrency: int = 5,
) -> None:
    """掲示板コメントを全ページ取得し {output_dir}/{horse_id}_{page}.txt に保存する。"""
    output_dir.mkdir(parents=True, exist_ok=True)

    # ページ1: 総ページ数の取得とコメント保存
    page = await context.new_page()
    try:
        await page.goto(
            f"https://db.netkeiba.com/?pid=horse_board&id={horse_id}"
        )
        await page.locator("#Comment_List").wait_for(timeout=15000)

        links = page.locator("a[href*='page=']")
        link_count = await links.count()
        page_nums = []
        for i in range(link_count):
            href = await links.nth(i).get_attribute("href") or ""
            m = re.search(r"page=(\d+)", href)
            if m:
                page_nums.append(int(m.group(1)))
        total_pages = max(page_nums) if page_nums else 1

        text = await page.locator("#Comment_List").inner_text()
        (output_dir / f"{horse_id}_1.txt").write_text(text, encoding="utf-8")
    finally:
        await page.close()

    if total_pages <= 1:
        return

    # ページ 2..N を Semaphore(concurrency) 下で並列取得
    sem = asyncio.Semaphore(concurrency)

    async def fetch_and_save(page_num: int) -> None:
        async with sem:
            text = await _fetch_comment_page(context, horse_id, page_num)
            (output_dir / f"{horse_id}_{page_num}.txt").write_text(
                text, encoding="utf-8"
            )

    results = await asyncio.gather(
        *[fetch_and_save(n) for n in range(2, total_pages + 1)],
        return_exceptions=True,
    )

    for page_num, result in zip(range(2, total_pages + 1), results):
        if isinstance(result, Exception):
            print(
                f"[warn] page {page_num} の取得失敗（スキップ）: {result}",
                file=sys.stderr,
            )


def _parse_comment_page(text: str) -> list[dict]:
    pattern = re.compile(
        r"\[(\d+)\][^\n]+\n\n(.*?)\n\n(\d{4}/\d+/\d+ \d+:\d+)",
        re.DOTALL,
    )
    return [
        {"no": int(m.group(1)), "date": m.group(3), "text": m.group(2).strip()}
        for m in pattern.finditer(text)
    ]


@with_retry(max_attempts=3, base_delay=1.0)
async def _fetch_comment_page(
    context: BrowserContext, horse_id: str, page_num: int
) -> str:
    page = await context.new_page()
    try:
        await page.goto(
            f"https://db.netkeiba.com/?pid=horse_board&id={horse_id}&page={page_num}"
        )
        await page.locator("#Comment_List").wait_for(timeout=15000)
        return await page.locator("#Comment_List").inner_text()
    finally:
        await page.close()
