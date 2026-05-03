import re
import sys

from playwright.async_api import BrowserContext

from netkeiba.retry import with_retry

_SEARCH_URL = "https://db.netkeiba.com/horse/search_detail.html"
_HORSE_ID_RE = re.compile(r"/horse/([0-9a-z]+)/?$")


async def get_horse_detail(context: BrowserContext, horse_id: str) -> dict:
    """馬IDから馬名・母馬名を取得する。"""
    page = await context.new_page()
    try:
        await _load_page(page, f"https://db.netkeiba.com/horse/{horse_id}/")

        # 馬名: 2番目の h1 (0番目は netkeiba ロゴ)
        name = (await page.locator("h1").nth(1).inner_text()).strip()

        # 母馬名: 血統表 row[2] 最初の td
        blood_table = page.get_by_role("table", name=re.compile("血統表"))
        mare = (
            await blood_table.locator("tr").nth(2).locator("td").first.inner_text()
        ).strip()

        return {"name": name, "mare": mare, "horse_id": horse_id}
    finally:
        await page.close()


async def search_horse(
    context: BrowserContext,
    *,
    name: str | None = None,
    mare: str | None = None,
    age: int | None = None,
) -> dict | list[dict]:
    """馬名または母馬名で馬を検索し、馬ID情報を返す。

    age を指定するとその年齢 from/to をフォームにセットする。
    age を省略するとフォームの初期値（from=2歳, to=指定なし）のまま検索する。

    Returns:
        単一ヒット (直接リダイレクト) → dict
        複数ヒット (list.html に遷移) → list[dict]  ※1件でも list
        該当なし → {"error": "該当データが存在しません"}
        想定外 URL → {"error": "想定外のページに遷移しました", "url": "..."}
    """
    page = await context.new_page()
    try:
        await _load_page(page, _SEARCH_URL)

        if age is not None:
            age_row = page.get_by_role("row", name=re.compile("年齢"))
            await age_row.get_by_role("combobox").nth(0).select_option(f"{age}歳")
            await age_row.get_by_role("combobox").nth(1).select_option(f"{age}歳")

        if name is not None:
            name_row = page.get_by_role("row", name=re.compile("馬名"))
            await name_row.get_by_role("textbox").fill(name)
            await name_row.get_by_role("combobox").select_option("に一致する")
        else:
            mare_row = page.get_by_role("row", name=re.compile("母名"))
            await mare_row.get_by_role("textbox").fill(mare)  # type: ignore[arg-type]

        # 検索ボタン (最後の "検 索" = 詳細検索フォームのもの)
        await page.get_by_role("button", name="検 索").last.click()
        await page.wait_for_load_state("domcontentloaded")

        url = page.url

        # パターン A: 直接 /horse/{id}/ にリダイレクト
        m = _HORSE_ID_RE.search(url)
        if m:
            horse_id = m.group(1)
            return await get_horse_detail(context, horse_id)

        # パターン B: list.html に遷移
        if "list.html" in url or "horse_list" in url:
            content = await page.content()
            if "該当データが存在しません" in content:
                return {"error": "該当データが存在しません"}
            return await _parse_list_results(context, page)

        # パターン C: 想定外 URL
        return {"error": "想定外のページに遷移しました", "url": url}

    finally:
        await page.close()


async def _parse_list_results(context: BrowserContext, page) -> list[dict]:
    """list.html の結果テーブルを解析し、各馬の詳細を返す。"""
    rows = page.locator("table.nk_tb_common tbody tr")
    count = await rows.count()
    results = []
    for i in range(count):
        row = rows.nth(i)
        link = row.locator("a[href*='/horse/']").first
        href = await link.get_attribute("href") or ""
        m = _HORSE_ID_RE.search(href)
        if not m:
            continue
        horse_id = m.group(1)
        try:
            detail = await get_horse_detail(context, horse_id)
        except Exception as e:
            print(f"[warn] {horse_id} の詳細取得失敗: {e}", file=sys.stderr)
            horse_name = (await link.inner_text()).strip()
            detail = {"name": horse_name, "mare": None, "horse_id": horse_id}
        results.append(detail)
    return results


@with_retry(max_attempts=3, base_delay=1.0)
async def _load_page(page, url: str) -> None:
    await page.goto(url)
    await page.wait_for_load_state("domcontentloaded")
