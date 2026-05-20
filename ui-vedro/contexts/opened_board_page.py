from typing import Any

import vedro
from d42 import fake
from playwright.async_api import Page

from interfaces.web.pages.board import BoardPage
from mocks import mocked_tasks_list
from schemas.tasks_list_response_schema import TasksListResponseSchema


@vedro.context
async def opened_board_page(
    page: Page,
    *,
    initial_tasks: dict[str, Any] | None = None,
) -> BoardPage:
    # Pin GET /api/tasks. If a test doesn't care about the initial fetch,
    # a fake-but-valid payload is generated.
    body = initial_tasks if initial_tasks is not None else fake(TasksListResponseSchema)

    # Keep the mock alive beyond __aenter__: search re-fetches must keep
    # resolving against the same dataset until a test overrides them.
    mock = mocked_tasks_list(page, body, wait_for_requests=None)
    await mock.__aenter__()

    board = BoardPage(page)
    await board.open()
    await board.task_counter.wait_for()
    return board
