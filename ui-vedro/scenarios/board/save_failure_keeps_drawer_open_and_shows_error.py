import vedro
from d42 import fake, validate_or_fail
from vedro_playwright import opened_browser_page

from contexts import opened_board_page, opened_create_task_drawer
from dicts import AllureID, Feature, Priority, Story, TaskStatus, allure_labels
from interfaces.web.pages.board import BoardPage
from mocks import mocked_create_task
from schemas import ValidTaskTitleSchema
from schemas.error_response_schema import ErrorResponseSchema
from schemas.task_schema import CreateTaskRequestSchema


@allure_labels(Feature.TaskEditor, Story.SaveErrors, Priority.Critical, AllureID("B-501"))
class Scenario(vedro.Scenario):
    # 500 on save: form keeps input, shows server message, re-enables Save.

    subject = "Save failure surfaces an error and keeps the drawer open with user input intact"

    async def given_browser_page(self):
        self.page = await opened_browser_page()

    async def given_form_input(self):
        self.title = fake(ValidTaskTitleSchema)
        self.expected_request = {
            "title": self.title,
            "description": "",
            "status": TaskStatus.Todo,
            "tags": [],
        }

    async def given_server_error_response(self):
        self.error_response = fake(ErrorResponseSchema % {
            "message": "Database temporarily unavailable. Try again in a moment.",
        })

    async def given_opened_board_page(self):
        self.board: BoardPage = await opened_board_page(
            self.page,
            initial_tasks={"data": [], "total": 0},
        )

    async def given_opened_create_task_drawer(self):
        await opened_create_task_drawer(self.board)

    async def given_filled_title(self):
        await self.board.task_drawer.title_input.fill(self.title)

    async def when_submit_form_against_failing_server(self):
        async with mocked_create_task(
            self.page, self.error_response, status=500
        ) as self.mock:
            await self.board.task_drawer.save_button.click()
            await self.board.task_drawer.drawer_error.wait_for()

    async def then_drawer_error_shows_server_message(self):
        assert await self.board.task_drawer.drawer_error.text() == \
            self.error_response["message"]

    async def and_request_body_was_what_user_typed(self):
        assert self.mock.history[0].body == self.expected_request
        validate_or_fail(CreateTaskRequestSchema, self.mock.history[0].body)

    async def and_drawer_remained_open_with_typed_title_intact(self):
        assert await self.board.task_drawer.title_input.value() == self.title

    async def and_save_button_is_re_enabled(self):
        disabled = await self.board.task_drawer.save_button.locator.get_attribute("disabled")
        assert disabled is None, (
            "Save button stayed disabled after a server error — the user is "
            "stuck unable to retry."
        )

    async def and_board_did_not_show_a_phantom_card(self):
        assert await self.board.task_list.visible_task_ids() == [], (
            "A failed save still mutated the board's task list — optimistic "
            "rendering must not survive a non-2xx response."
        )
