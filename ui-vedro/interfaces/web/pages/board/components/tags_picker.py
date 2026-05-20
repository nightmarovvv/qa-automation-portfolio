from __future__ import annotations

from interfaces.web.web_elements import BaseElement
from interfaces.web.web_elements.mixins import Clickable


# Multi-select chips. Selected state is exposed via aria-pressed,
# which is what we assert against.
class TagsPicker(BaseElement):

    LOCATOR_NAME = "tags-picker"

    class _ListTagItem(BaseElement, Clickable):
        def __init__(self, parent: TagsPicker, slug: str):
            super().__init__(parent, data_test=f"tag-chip-{slug}")
            self._slug = slug

        @property
        def slug(self) -> str:
            return self._slug

        async def is_selected(self) -> bool:
            value = await self.locator.get_attribute("aria-pressed")
            return value == "true"

    def get_list_tag_by_slug(self, slug: str) -> _ListTagItem:
        return self._ListTagItem(self, slug=slug)
