from __future__ import annotations

from interfaces.web.pages.board.components.tags_picker import TagsPicker
from interfaces.web.web_elements import BaseButton, BaseElement, BaseInput, BaseText


# Slide-out form for create + edit. Visibility is the `hidden` attribute
# on the aside; wait_for() reflects that.
class TaskDrawer(BaseElement):

    LOCATOR_NAME = "task-drawer"

    @property
    def title_text(self) -> BaseText:
        return BaseText(self, data_test="drawer-title")

    @property
    def title_input(self) -> BaseInput:
        return BaseInput(self, data_test="task-title-input")

    @property
    def description_input(self) -> BaseInput:
        return BaseInput(self, data_test="task-description-input")

    @property
    def status_select(self) -> BaseElement:
        return BaseElement(self, data_test="task-status-select")

    async def select_status(self, value: str) -> None:
        await self.status_select.locator.select_option(value=value)

    @property
    def tags_picker(self) -> TagsPicker:
        return TagsPicker(self)

    @property
    def title_error(self) -> BaseText:
        return BaseText(self, data_test="task-title-error")

    @property
    def drawer_error(self) -> BaseText:
        return BaseText(self, data_test="drawer-error")

    @property
    def cancel_button(self) -> BaseButton:
        return BaseButton(self, data_test="drawer-cancel")

    @property
    def close_button(self) -> BaseButton:
        return BaseButton(self, data_test="drawer-close")

    @property
    def save_button(self) -> BaseButton:
        return BaseButton(self, data_test="drawer-save")
