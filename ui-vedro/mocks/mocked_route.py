# Async context manager over page.route(). Records every matching
# request into .history and on exit asserts the count matches the
# expected wait_for_requests. The mock-server-style API (response_body
# pre-built by the test, count check on exit) keeps tests honest about
# what the UI actually called.

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import parse_qsl, urlsplit

from playwright.async_api import Page, Route


@dataclass(frozen=True)
class RecordedRequest:
    method: str
    url: str
    path: str
    query: dict[str, str]
    headers: dict[str, str]
    body: Any

    @classmethod
    def from_route(cls, route: Route) -> RecordedRequest:
        req = route.request
        parts = urlsplit(req.url)
        try:
            body: Any = req.post_data_json
        except Exception:
            body = req.post_data
        return cls(
            method=req.method,
            url=req.url,
            path=parts.path,
            query=dict(parse_qsl(parts.query, keep_blank_values=True)),
            headers={k.lower(): v for k, v in req.headers.items()},
            body=body,
        )


class MockedRoute:
    # url_pattern: substring or compiled regex (substring is matched against
    #              the full URL — keep specific, "/api/tasks" not "/tasks")
    # response_body: pre-built JSON (dict/list); build it from a d42 schema
    # wait_for_requests: expected number of matching calls; mismatch on
    #                    __aexit__ raises. Pass None to skip the count check.

    def __init__(
        self,
        page: Page,
        url_pattern: str | re.Pattern[str],
        *,
        method: str = "GET",
        status: int = 200,
        response_body: Any,
        wait_for_requests: int | None = 1,
    ):
        self._page = page
        self._method = method.upper()
        self._status = status
        self._response_body = response_body
        self._wait_for_requests = wait_for_requests
        self._matcher = self._build_matcher(url_pattern)
        self._history: list[RecordedRequest] = []

    @property
    def history(self) -> list[RecordedRequest]:
        return self._history

    @staticmethod
    def _build_matcher(pattern: str | re.Pattern[str]):
        if isinstance(pattern, re.Pattern):
            return lambda url: bool(pattern.search(url))
        return lambda url: pattern in url

    async def _handle(self, route: Route) -> None:
        if route.request.method != self._method or not self._matcher(route.request.url):
            await route.fallback()
            return
        self._history.append(RecordedRequest.from_route(route))
        await route.fulfill(
            status=self._status,
            content_type="application/json",
            body=json.dumps(self._response_body, default=str),
        )

    async def __aenter__(self) -> MockedRoute:
        await self._page.route("**/*", self._handle)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self._page.unroute("**/*", self._handle)
        if exc_type is not None or self._wait_for_requests is None:
            return
        actual = len(self._history)
        if actual != self._wait_for_requests:
            raise AssertionError(
                f"Mock expected {self._wait_for_requests} {self._method} call(s), "
                f"got {actual}. Recorded URLs: {[r.url for r in self._history]}"
            )
