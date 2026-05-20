import vedro
from d42 import fake, validate_or_fail
from vedro_playwright import opened_browser_page

from contexts import opened_board_page, opened_edit_task_drawer
from dicts import AllureID, Feature, Priority, Story, Tag, allure_labels
from interfaces.web.pages.board import BoardPage
from mocks import mocked_update_task
from schemas import ValidIDSchema
from schemas.task_schema import TaskSchema, UpdateTaskRequestSchema


@allure_labels(Feature.TaskEditor, Story.EditTask, Priority.Critical, AllureID("B-201"))
class Scenario(vedro.Scenario):
    subject = "Edit a task and re-select its tags from the drawer's multi-select"

    async def given_browser_page(self):
        self.page = await opened_browser_page()

    async def given_existing_task_with_one_tag(self):
        self.task_id = fake(ValidIDSchema)
        self.task = fake(TaskSchema % {
            "id": self.task_id,
            "tags": [Tag.Bug],
        })

    async def given_target_tags(self):
        # Start with [Bug]; the user un-toggles Bug and picks Frontend + Infra.
        self.tags_to_remove = [Tag.Bug]
        self.tags_to_add = [Tag.Frontend, Tag.Infra]
        self.expected_tags = sorted(self.tags_to_add)

    async def given_server_response_for_the_update(self):
        self.updated_task = fake(TaskSchema % {
            "id": self.task_id,
            "title": self.task["title"],
            "tags": self.expected_tags,
        })

    async def given_opened_board_page_with_one_task(self):
        self.board: BoardPage = await opened_board_page(
            self.page,
            initial_tasks={"data": [self.task], "total": 1},
        )

    async def given_opened_edit_drawer(self):
        await opened_edit_task_drawer(self.board, self.task_id)

    async def given_initial_tag_is_pre_selected(self):
        chip = self.board.task_drawer.tags_picker.get_list_tag_by_slug(Tag.Bug)
        assert await chip.is_selected(), (
            "Drawer didn't hydrate the task's existing tags into the picker — "
            "edit mode would be silently destructive."
        )

    async def when_re_select_tags_and_save(self):
        picker = self.board.task_drawer.tags_picker
        for tag in self.tags_to_remove:
            await picker.get_list_tag_by_slug(tag).click()
        for tag in self.tags_to_add:
            await picker.get_list_tag_by_slug(tag).click()
        async with mocked_update_task(
            self.page, self.task_id, self.updated_task
        ) as self.mock:
            await self.board.task_drawer.save_button.click()
            await self.board.task_drawer.wait_for(state="hidden")

    async def then_request_body_has_sorted_tag_set(self):
        assert self.mock.history[0].body["tags"] == self.expected_tags

    async def and_request_body_satisfies_published_contract(self):
        validate_or_fail(UpdateTaskRequestSchema, self.mock.history[0].body)

    async def and_card_re_renders_with_the_new_tag_chips(self):
        card = self.board.task_list.get_list_task_by_id(self.task_id)
        await card.wait_for()
        rendered_tags = await card.locator.locator(
            '[data-test^="task-tag-"]'
        ).evaluate_all("nodes => nodes.map(n => n.textContent.trim())")
        assert sorted(rendered_tags) == self.expected_tags
