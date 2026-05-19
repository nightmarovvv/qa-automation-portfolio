from __future__ import annotations

from playwright.async_api import Page as PlaywrightPage

from config import app
from interfaces.web.web_elements import BaseButton, BaseInput, BaseText


class Header:
    def __init__(self, page: PlaywrightPage):
        self._page = page

    @property
    def brand_link(self) -> BaseButton:
        return BaseButton(self._page, data_test="brand")

    @property
    def search_input(self) -> BaseInput:
        return BaseInput(self._page, data_test="search-input")

    @property
    def create_task_button(self) -> BaseButton:
        return BaseButton(self._page, data_test="create-task-button")


class Toast:
    @staticmethod
    def of(page: PlaywrightPage) -> BaseText:
        return BaseText(page, data_test="toast")


# RELATIVE_URL is joined with app.base_url in .open().
# Cross-page chrome (header, toast) lives here; page-specific stuff goes
# into subclasses.
class BasePage:

    RELATIVE_URL: str = ""
    NAVIGATION_TIMEOUT_MS = 30_000  # headroom for cold starts on demo deploys

    def __init__(self, page: PlaywrightPage):
        self._page = page

    @property
    def raw(self) -> PlaywrightPage:
        return self._page

    @property
    def header(self) -> Header:
        return Header(self._page)

    @property
    def toast(self) -> BaseText:
        return Toast.of(self._page)

    async def open(self) -> None:
        url = app.base_url.rstrip("/") + "/" + self.RELATIVE_URL.lstrip("/")
        await self._page.goto(
            url, wait_until="domcontentloaded", timeout=self.NAVIGATION_TIMEOUT_MS
        )
