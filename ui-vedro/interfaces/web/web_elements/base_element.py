from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.async_api import Locator, Page


# data-test only. CSS/xpath is forbidden by convention — if an element
# is missing data-test, get the dev team to add one.
class BaseElement:

    LOCATOR_NAME: str = ""

    def __init__(self, parent: BaseElement | Page, data_test: str | None = None):
        self._parent = parent
        self._data_test = data_test or self.LOCATOR_NAME
        if not self._data_test:
            raise ValueError(
                f"{type(self).__name__}: data-test is empty. "
                "Set LOCATOR_NAME on the class or pass data_test explicitly."
            )

    @property
    def locator(self) -> Locator:
        scope = self._parent.locator if isinstance(self._parent, BaseElement) else self._parent
        return scope.locator(f'[data-test="{self._data_test}"]')

    async def is_visible(self) -> bool:
        return await self.locator.is_visible()

    async def is_hidden(self) -> bool:
        return await self.locator.is_hidden()

    async def wait_for(self, state: str = "visible", timeout: int | None = None) -> None:
        await self.locator.wait_for(state=state, timeout=timeout)

    async def scroll_into_view(self) -> None:
        await self.locator.scroll_into_view_if_needed()

    async def count(self) -> int:
        return await self.locator.count()
