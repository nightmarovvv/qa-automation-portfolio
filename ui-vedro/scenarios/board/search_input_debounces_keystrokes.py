import vedro
from d42 import fake
from vedro_playwright import opened_browser_page

from contexts import opened_board_page
from dicts import AllureID, Feature, Priority, Story, allure_labels
from interfaces.web.pages.board import BoardPage
from mocks import mocked_tasks_list
from schemas import ValidIDSchema
from schemas.task_schema import TaskSchema


@allure_labels(Feature.Search, Story.Search, Priority.Critical, AllureID("B-301"))
class Scenario(vedro.Scenario):
    # loadTasks is wrapped in a 300ms debounce. Type 5 chars fast and
    # assert the backend was hit exactly once.
    subject = "Search input debounces keystrokes and fires a single backend call"

    async def given_browser_page(self):
        self.page = await opened_browser_page()

    async def given_search_query(self):
        self.query = "alpha"  # five characters, typed one by one below

    async def given_matching_task(self):
        self.matching_task_id = fake(ValidIDSchema)
        self.search_response = {
            "data": [fake(TaskSchema % {
                "id": self.matching_task_id,
                "title": "Alpha launch retrospective",
            })],
            "total": 1,
        }

    async def given_opened_board_page(self):
        self.board: BoardPage = await opened_board_page(
            self.page,
            initial_tasks={"data": [], "total": 0},
        )

    async def when_user_types_search_query_character_by_character(self):
        async with mocked_tasks_list(
            self.page, self.search_response, wait_for_requests=None
        ) as self.search_mock:
            await self.board.header.search_input.type(self.query, delay_ms=40)
            # The debounce is 300 ms; wait until the matching card appears
            # so the test deterministically reaches the post-fire state.
            await self.board.task_list.get_list_task_by_id(
                self.matching_task_id
            ).wait_for()

    async def then_exactly_one_backend_call_was_made(self):
        actual = len(self.search_mock.history)
        assert actual == 1, (
            f"Expected debounce to coalesce {len(self.query)} keystrokes into "
            f"one request, but the mock recorded {actual} calls: "
            f"{[r.url for r in self.search_mock.history]}."
        )

    async def and_the_request_carried_the_full_query(self):
        assert self.search_mock.history[0].query == {"q": self.query}
