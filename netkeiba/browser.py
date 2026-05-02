from contextlib import asynccontextmanager
from typing import AsyncIterator

from playwright.async_api import BrowserContext, async_playwright


@asynccontextmanager
async def browser_context(headless: bool = True) -> AsyncIterator[BrowserContext]:
    """headless Chromium を起動し BrowserContext を yield。終了時に自動クリーン。"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        ctx = await browser.new_context()
        try:
            yield ctx
        finally:
            await ctx.close()
            await browser.close()
