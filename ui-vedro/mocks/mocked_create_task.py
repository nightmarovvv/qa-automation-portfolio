from typing import Any

from playwright.async_api import Page

from mocks.mocked_route import MockedRoute


def mocked_create_task(
    page: Page,
    response_body: dict[str, Any],
    *,
    status: int = 201,
    wait_for_requests: int | None = 1,
) -> MockedRoute:
    """Mock `POST /api/tasks` — drawer's submit when creating a new task.

    The `response_body` is the persisted task that the SPA upserts into
    its in-memory list, so it must satisfy `TaskSchema`.
    """
    return MockedRoute(
        page,
        url_pattern="/api/tasks",
        method="POST",
        status=status,
        response_body=response_body,
        wait_for_requests=wait_for_requests,
    )
