from interfaces.web.web_elements.base_element import BaseElement
from interfaces.web.web_elements.mixins import Clickable, Textable


class BaseInput(BaseElement, Textable, Clickable):
    """Standard `<input>` / `<textarea>` element.

    For `contenteditable` containers or code editors (Monaco, CodeMirror)
    do NOT inherit from this — they react to typing differently and don't
    expose `value`. Use `(BaseElement, Clickable, Textable)` directly and
    override `value()` to read DOM text.
    """

    async def error_text(self) -> str | None:
        """Adjacent inline error rendered by the form. Returns None if absent."""
        sibling = self.locator.locator("xpath=following-sibling::*[1]")
        if await sibling.count() == 0:
            return None
        text = await sibling.text_content()
        return (text or "").strip() or None
