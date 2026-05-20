import re
from typing import Any

from playwright.async_api import Page

from mocks.mocked_route import MockedRoute


def mocked_update_task(
    page: Page,
    task_id: str,
    response_body: dict[str, Any],
    *,
    status: int = 200,
    wait_for_requests: int | None = 1,
) -> MockedRoute:
    """Mock `PATCH /api/tasks/{id}` for a specific task id."""
    # Scope the matcher to the exact id — adjacent PATCH calls (different
    # task) should fall through rather than poison this mock's history.
    pattern = re.compile(rf"/api/tasks/{re.escape(task_id)}(?:\?|$)")
    return MockedRoute(
        page,
        url_pattern=pattern,
        method="PATCH",
        status=status,
        response_body=response_body,
        wait_for_requests=wait_for_requests,
    )
