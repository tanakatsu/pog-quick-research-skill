from playwright.async_api import BrowserContext


async def fetch_horse_info(context: BrowserContext, horse_id: str) -> dict:
    raise NotImplementedError
