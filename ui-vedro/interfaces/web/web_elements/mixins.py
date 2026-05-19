from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.async_api import Locator


class _LocatorHolder:
    """Type stub so mixins can declare what they expect from the host element."""

    @property
    def locator(self) -> Locator: ...  # pragma: no cover


class Clickable(_LocatorHolder):
    async def click(self) -> None:
        await self.locator.click()

    async def hover(self) -> None:
        await self.locator.hover()


class Textable(_LocatorHolder):
    async def fill(self, value: str) -> None:
        await self.locator.fill(value)

    async def type(self, value: str, *, delay_ms: int = 30) -> None:
        """Use only when the app relies on per-keystroke handlers (debounced
        search, masked inputs). `fill` is faster and equivalent for plain inputs.
        """
        await self.locator.press_sequentially(value, delay=delay_ms)

    async def clear(self) -> None:
        await self.locator.fill("")

    async def value(self) -> str:
        return await self.locator.input_value()


class Readable(_LocatorHolder):
    async def text(self) -> str:
        raw = await self.locator.text_content()
        return (raw or "").strip()

    async def inner_text(self) -> str:
        return (await self.locator.inner_text()).strip()
