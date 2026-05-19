"""Snap a few screenshots of the live Allure report.

Used once to populate docs/img/. Re-run after major CI changes to refresh.
"""
import asyncio
from pathlib import Path

from playwright.async_api import async_playwright


REPORT_URL = "https://nightmarovvv.github.io/qa-automation-portfolio/"
OUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "img"


async def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        await page.goto(REPORT_URL, wait_until="networkidle")
        await page.wait_for_timeout(2500)
        await page.screenshot(path=str(OUT_DIR / "allure-overview.png"))

        await page.goto(REPORT_URL + "#suites", wait_until="networkidle")
        await page.wait_for_timeout(2000)
        for _ in range(5):
            nodes = page.locator(".node__title")
            n = await nodes.count()
            if n == 0:
                break
            for i in range(n):
                try:
                    await nodes.nth(i).click(timeout=500)
                except Exception:
                    pass
            await page.wait_for_timeout(300)
        await page.screenshot(
            path=str(OUT_DIR / "allure-suites.png"),
            full_page=True,
        )

        await page.goto(REPORT_URL + "#behaviors", wait_until="networkidle")
        await page.wait_for_timeout(2000)
        # toggle every collapsed node (allure uses .node__title for that)
        for _ in range(5):
            nodes = page.locator(".node__title")
            n = await nodes.count()
            if n == 0:
                break
            for i in range(n):
                try:
                    await nodes.nth(i).click(timeout=500)
                except Exception:
                    pass
            await page.wait_for_timeout(300)
        await page.screenshot(
            path=str(OUT_DIR / "allure-behaviors.png"),
            full_page=True,
        )

        # graphs view
        await page.goto(REPORT_URL + "#graph", wait_until="networkidle")
        await page.wait_for_timeout(2500)
        await page.screenshot(path=str(OUT_DIR / "allure-graphs.png"))

        await browser.close()
    print("ok:", *(p.name for p in OUT_DIR.glob("*.png")))


if __name__ == "__main__":
    asyncio.run(main())
