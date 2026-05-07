from playwright.async_api import BrowserContext


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
    raise NotImplementedError
