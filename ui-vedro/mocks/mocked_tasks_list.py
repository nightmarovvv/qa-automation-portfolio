from typing import Any

from playwright.async_api import Page

from mocks.mocked_route import MockedRoute


def mocked_tasks_list(
    page: Page,
    response_body: dict[str, Any],
    *,
    wait_for_requests: int | None = 1,
) -> MockedRoute:
    """Mock `GET /api/tasks` (with or without `?q=` filtering).

    Pass ``wait_for_requests=None`` when the test goes through several
    fetches in one drawer flow and the exact count isn't load-bearing.
    """
    return MockedRoute(
        page,
        url_pattern="/api/tasks",
        method="GET",
        response_body=response_body,
        wait_for_requests=wait_for_requests,
    )
