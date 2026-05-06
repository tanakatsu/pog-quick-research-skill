import asyncio
import re
import sys
from pathlib import Path

from playwright.async_api import BrowserContext

from netkeiba.retry import with_retry


async def fetch_all_board_comments(
    context: BrowserContext,
    horse_id: str,
    concurrency: int = 5,
) -> list[dict]:
    """掲示板コメントを全ページ取得してパース済みコメント一覧を返す。"""
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
        page1_comments = _parse_comment_page(text)
        print(f"ページ 1/{total_pages} 完了")
    finally:
        await page.close()

    if total_pages <= 1:
        return page1_comments

    sem = asyncio.Semaphore(concurrency)

    async def fetch_page(page_num: int) -> list[dict]:
        async with sem:
            text = await _fetch_comment_page(context, horse_id, page_num)
            comments = _parse_comment_page(text)
            print(f"ページ {page_num}/{total_pages} 完了")
            return comments

    results = await asyncio.gather(
        *[fetch_page(n) for n in range(2, total_pages + 1)],
        return_exceptions=True,
    )

    all_comments = list(page1_comments)
    for page_num, result in zip(range(2, total_pages + 1), results):
        if isinstance(result, BaseException):
            print(
                f"[warn] page {page_num} の取得失敗（スキップ）: {result}",
                file=sys.stderr,
            )
        else:
            all_comments.extend(result)

    return all_comments


_COMMENT_RE = re.compile(
    r"\[(\d+)\][^\n]+\n\n(.*?)\n\n(\d{4}/\d+/\d+ \d+:\d+)",
    re.DOTALL,
)


def _parse_comment_page(text: str) -> list[dict]:
    return [
        {"no": int(m.group(1)), "date": m.group(3), "text": m.group(2).strip()}
        for m in _COMMENT_RE.finditer(text)
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
