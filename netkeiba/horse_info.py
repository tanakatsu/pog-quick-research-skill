import re

from playwright.async_api import BrowserContext

from netkeiba.retry import with_retry

_HORSE_ID_RE = re.compile(r"/horse/(?:ped/)?([0-9a-z]+)/?")

_PROF_LABEL_MAP = {
    "生年月日": "birth_date",
    "調教師": "trainer",
    "馬主": "owner",
    "生産者": "breeder",
    "セリ取引価格": "purchase_price",
    "募集情報": "subscription_price",
    "獲得賞金 (中央)": "prize_money",
    "獲得賞金 (地方)": "prize_money_nra",
    "通算成績": "career_record",
}


async def fetch_horse_info(context: BrowserContext, horse_id: str) -> dict:
    """馬詳細ページから馬情報を取得する。

    Returns:
        {
            "name": str, "sex": str | None, "birth_date": str | None,
            "sire": str | None, "mare": str | None, "mare_id": str | None,
            "bms": str | None, "trainer": str | None, "owner": str | None,
            "breeder": str | None, "subscription_price": str | None,
            "purchase_price": str | None, "prize_money": str | None,
            "prize_money_nra": str | None, "career_record": str | None,
            "notable_wins": list[str] | None, "close_relative": list[str] | None,
        }
    """
    page = await context.new_page()
    try:
        await _load_page(page, f"https://db.netkeiba.com/horse/{horse_id}")

        # 馬名: 2番目の h1 (0番目は netkeiba ロゴ)
        name = (await page.locator("h1").nth(1).inner_text()).strip()

        # 性別: p.txt_01 の最初のトークン (例: "牝　栗毛" → "牝")
        sex = await _safe_text(page.locator("p.txt_01").first)
        if sex:
            sex = sex.split()[0] if sex.split() else None

        # プロフィールテーブル
        prof: dict = {}
        rows = page.locator("table.db_prof_table tr")
        count = await rows.count()
        for i in range(count):
            row = rows.nth(i)
            th_loc = row.locator("th")
            td_loc = row.locator("td").first
            if await th_loc.count() == 0 or await td_loc.count() == 0:
                continue
            label = (await th_loc.inner_text()).strip()
            key = _PROF_LABEL_MAP.get(label)
            if key is None:
                continue
            value = (await td_loc.inner_text()).strip()
            # "-" はデータなし扱い
            prof[key] = value if value and value != "-" else None

        # 主な勝鞍: db_prof_table の th=主な勝鞍 の td 内リンクテキストリスト
        notable_wins = await _parse_prof_table_links(page, "主な勝鞍")
        # 近親馬: db_prof_table の th=近親馬 の td 内リンクテキストリスト
        close_relative = await _parse_prof_table_links(page, "近親馬")

        # 血統表から父・母・母父を取得
        sire, mare, mare_id, bms = await _parse_blood_table(page)

        return {
            "name": name,
            "sex": sex,
            "birth_date": prof.get("birth_date"),
            "sire": sire,
            "mare": mare,
            "mare_id": mare_id,
            "bms": bms,
            "trainer": prof.get("trainer"),
            "owner": prof.get("owner"),
            "breeder": prof.get("breeder"),
            "subscription_price": prof.get("subscription_price"),
            "purchase_price": prof.get("purchase_price"),
            "prize_money": prof.get("prize_money"),
            "prize_money_nra": prof.get("prize_money_nra"),
            "career_record": prof.get("career_record"),
            "notable_wins": notable_wins,
            "close_relative": close_relative,
        }
    finally:
        await page.close()


async def _parse_blood_table(page) -> tuple[str | None, str | None, str | None, str | None]:
    """血統表から父・母・母父と母IDを返す。

    blood_table の行構成:
      tr[0]: td.b_ml (父, rowspan=2) + td.b_ml (父の父)
      tr[1]: td.b_fml (父の母)
      tr[2]: td.b_fml (母, rowspan=2) + td.b_ml (母の父=BMS)
      tr[3]: td.b_fml (母の母)
    """
    try:
        blood_table = page.locator("table.blood_table")
        if await blood_table.count() == 0:
            return None, None, None, None

        trs = blood_table.locator("tr")
        if await trs.count() < 3:
            return None, None, None, None

        # 父
        sire_td = trs.nth(0).locator("td.b_ml").first
        sire = (await sire_td.inner_text()).strip() or None

        # 母
        mare_td = trs.nth(2).locator("td.b_fml").first
        mare = (await mare_td.inner_text()).strip() or None

        # 母ID
        mare_id = None
        mare_link = mare_td.locator("a[href*='/horse/']").first
        if await mare_link.count() > 0:
            href = await mare_link.get_attribute("href") or ""
            m = _HORSE_ID_RE.search(href)
            mare_id = m.group(1) if m else None

        # 母の父 (BMS): tr[2] の2番目の td
        bms_td = trs.nth(2).locator("td").nth(1)
        bms = None
        if await bms_td.count() > 0:
            bms = (await bms_td.inner_text()).strip() or None

        return sire, mare, mare_id, bms
    except Exception:
        return None, None, None, None


async def _parse_prof_table_links(page, heading_text: str) -> list[str] | None:
    """db_prof_table の th=heading_text に対応する td 内リンクテキストリストを返す。

    リンクが存在しないか空の場合は None を返す。
    """
    try:
        rows = page.locator("table.db_prof_table tr")
        count = await rows.count()
        for i in range(count):
            row = rows.nth(i)
            th_loc = row.locator("th")
            if await th_loc.count() == 0:
                continue
            label = (await th_loc.inner_text()).strip()
            if label != heading_text:
                continue
            td_loc = row.locator("td").first
            if await td_loc.count() == 0:
                return None
            links = td_loc.locator("a")
            link_count = await links.count()
            items = []
            for j in range(link_count):
                text = (await links.nth(j).inner_text()).strip()
                href = await links.nth(j).get_attribute("href") or ""
                # 空リンク (href="/race//" など) はスキップ
                if text and href and not href.endswith("//"):
                    items.append(text)
            return items if items else None
        return None
    except Exception:
        return None


async def _safe_text(locator) -> str | None:
    try:
        if await locator.count() == 0:
            return None
        text = (await locator.inner_text()).strip()
        return text or None
    except Exception:
        return None


@with_retry(max_attempts=3, base_delay=1.0)
async def _load_page(page, url: str) -> None:
    await page.goto(url)
    await page.wait_for_load_state("domcontentloaded")
