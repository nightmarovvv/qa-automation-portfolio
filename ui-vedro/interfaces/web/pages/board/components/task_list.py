from __future__ import annotations

import re

from interfaces.web.web_elements import BaseElement, BaseText


# Cards live at [data-test="task-<ULID>"]. Address by id, not by index —
# API may reorder results between renders but the ULID is stable.
class TaskList(BaseElement):

    LOCATOR_NAME = "task-list"

    _ID_PATTERN = re.compile(r"^task-([0-9A-HJKMNP-TV-Z]{26})$")

    class _ListTaskItem(BaseElement):
        def __init__(self, parent: TaskList, task_id: str):
            super().__init__(parent, data_test=f"task-{task_id}")
            self._task_id = task_id

        @property
        def task_id(self) -> str:
            return self._task_id

        @property
        def title(self) -> BaseText:
            return BaseText(self, data_test="task-title")

        @property
        def status(self) -> BaseText:
            return BaseText(self, data_test="task-status")

        @property
        def tags_container(self) -> BaseText:
            return BaseText(self, data_test="task-tags")

        async def click(self) -> None:
            await self.locator.click()

    def get_list_task_by_id(self, task_id: str) -> _ListTaskItem:
        return self._ListTaskItem(self, task_id=task_id)

    async def visible_task_ids(self) -> list[str]:
        attrs = await self.locator.locator('[data-test^="task-"]').evaluate_all(
            "nodes => nodes.map(n => n.getAttribute('data-test'))"
        )
        ids: list[str] = []
        for value in attrs or []:
            if not value:
                continue
            match = self._ID_PATTERN.match(value)
            if match:
                ids.append(match.group(1))
        return ids
