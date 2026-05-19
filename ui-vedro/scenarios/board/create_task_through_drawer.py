import vedro
from d42 import fake, validate_or_fail
from vedro_playwright import opened_browser_page

from contexts import opened_board_page, opened_create_task_drawer
from dicts import AllureID, Feature, Priority, Story, Tag, TaskStatus, Translations, allure_labels
from interfaces.web.pages.board import BoardPage
from mocks import mocked_create_task
from schemas import ValidIDSchema, ValidTaskTitleSchema
from schemas.task_schema import CreateTaskRequestSchema, TaskSchema


@allure_labels(Feature.Board, Story.CreateTask, Priority.Blocker, AllureID("B-101"))
class Scenario(vedro.Scenario):
    subject = "Create a task through the drawer and see it on the board"

    async def given_browser_page(self):
        self.page = await opened_browser_page()

    async def given_task_payload(self):
        self.title = fake(ValidTaskTitleSchema)
        self.tags = [Tag.Frontend, Tag.Bug]
        self.expected_request = {
            "title": self.title,
            "description": "",
            "status": TaskStatus.InProgress,
            "tags": sorted(self.tags),
        }

    async def given_server_response_for_the_new_task(self):
        self.new_task_id = fake(ValidIDSchema)
        self.created_task = fake(TaskSchema % {
            "id": self.new_task_id,
            "title": self.title,
            "description": "",
            "status": TaskStatus.InProgress,
            "tags": sorted(self.tags),
        })

    async def given_opened_board_page(self):
        self.board: BoardPage = await opened_board_page(
            self.page,
            initial_tasks={"data": [], "total": 0},
        )

    async def given_opened_create_task_drawer(self):
        await opened_create_task_drawer(self.board)

    async def given_filled_form(self):
        drawer = self.board.task_drawer
        await drawer.title_input.fill(self.title)
        await drawer.select_status(TaskStatus.InProgress)
        for tag in self.tags:
            await drawer.tags_picker.get_list_tag_by_slug(tag).click()

    async def when_submit_form(self):
        async with mocked_create_task(self.page, self.created_task) as self.mock:
            await self.board.task_drawer.save_button.click()
            await self.board.task_list.get_list_task_by_id(self.new_task_id).wait_for()

    async def then_drawer_closed(self):
        await self.board.task_drawer.wait_for(state="hidden")

    async def and_request_body_matches_what_user_typed(self):
        assert self.mock.history[0].body == self.expected_request

    async def and_request_body_satisfies_published_contract(self):
        validate_or_fail(CreateTaskRequestSchema, self.mock.history[0].body)

    async def and_card_renders_with_typed_title(self):
        card = self.board.task_list.get_list_task_by_id(self.new_task_id)
        assert await card.title.text() == self.title

    async def and_toast_confirms_creation(self):
        assert await self.board.toast.text() == Translations.ToastCreated
