"""Record a demo of the SPA being driven by a scripted scenario.

Produces docs/img/demo-create-task.gif by capturing PNG frames at key
moments and stitching them via Pillow. No ffmpeg required.
"""
import asyncio
import io
import json
import socket
import subprocess
import sys
from pathlib import Path

from PIL import Image
from playwright.async_api import async_playwright


REPO = Path(__file__).resolve().parent.parent
APP_DIR = REPO / "app"
OUT_DIR = REPO / "docs" / "img"


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


async def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    port = free_port()
    spa = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"],
        cwd=str(APP_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    frames: list[Image.Image] = []

    async def snap(page, hold_ms: int = 0):
        if hold_ms:
            await page.wait_for_timeout(hold_ms)
        buf = await page.screenshot(type="png")
        frames.append(Image.open(io.BytesIO(buf)).convert("P", palette=Image.ADAPTIVE))

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context(viewport={"width": 1100, "height": 700})
            page = await context.new_page()

            await page.route(
                "**/api/tasks*",
                lambda route: route.fulfill(
                    status=200,
                    content_type="application/json",
                    body=json.dumps({"data": [], "total": 0}),
                ),
            )

            created = {
                "id": "01HZZZAAAAAAAAAAAAAAAAAAAA",
                "title": "Polish portfolio repo",
                "description": "Add screenshots and demo gif to the README",
                "status": "in_progress",
                "tags": ["frontend", "research"],
                "created_at": "2026-05-19T20:00:00Z",
                "updated_at": "2026-05-19T20:00:00Z",
            }

            async def post_handler(route):
                if route.request.method == "POST":
                    await route.fulfill(
                        status=201,
                        content_type="application/json",
                        body=json.dumps(created),
                    )
                else:
                    await route.fallback()

            await page.route("**/api/tasks", post_handler)

            await page.goto(f"http://127.0.0.1:{port}/")
            await page.locator('[data-test="task-counter"]').wait_for()
            await snap(page, 400)  # 1: empty board

            await page.locator('[data-test="create-task-button"]').click()
            await page.locator('[data-test="task-title-input"]').wait_for()
            await snap(page, 350)  # 2: drawer open

            await page.locator('[data-test="task-title-input"]').fill(created["title"])
            await snap(page, 250)  # 3: title typed

            await page.locator('[data-test="task-description-input"]').fill(
                created["description"]
            )
            await snap(page, 250)  # 4: description typed

            await page.locator('[data-test="task-status-select"]').select_option(
                value="in_progress"
            )
            await snap(page, 250)  # 5: status picked

            await page.locator('[data-test="tag-chip-frontend"]').click()
            await page.locator('[data-test="tag-chip-research"]').click()
            await snap(page, 350)  # 6: tags picked

            await page.locator('[data-test="drawer-save"]').click()
            await page.locator(f'[data-test="task-{created["id"]}"]').wait_for()
            await snap(page, 500)  # 7: card lands + toast

            await snap(page, 1100)  # 8: hold final frame longer

            await context.close()
            await browser.close()

        gif_path = OUT_DIR / "demo-create-task.gif"
        # downscale to keep the gif small
        target_w = 900
        scaled = []
        for f in frames:
            w, h = f.size
            new_h = int(h * target_w / w)
            scaled.append(
                f.resize((target_w, new_h), Image.LANCZOS).convert(
                    "P", palette=Image.ADAPTIVE
                )
            )
        # per-frame durations (ms): give later frames a bit more breathing room
        durations = [900, 700, 700, 700, 700, 800, 1100, 1500][: len(scaled)]
        scaled[0].save(
            gif_path,
            save_all=True,
            append_images=scaled[1:],
            duration=durations,
            loop=0,
            disposal=2,
            optimize=True,
        )
        print(f"ok: {gif_path}  size={gif_path.stat().st_size:,}B  frames={len(scaled)}")
    finally:
        spa.terminate()
        try:
            spa.wait(timeout=3)
        except subprocess.TimeoutExpired:
            spa.kill()


if __name__ == "__main__":
    asyncio.run(main())
