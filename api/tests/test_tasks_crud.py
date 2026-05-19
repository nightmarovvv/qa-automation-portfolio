import allure
import pytest


@allure.feature("Tasks")
@allure.story("CRUD")
@pytest.mark.usefixtures("clean_tasks")
class TestTasksCRUD:

    @allure.title("Create task -> 201 with normalized payload")
    @pytest.mark.smoke
    def test_create_task(self, api_manager):
        r = api_manager.tasks.create(
            title="Write release notes",
            description="for 0.4.0",
            status="todo",
            tags=["frontend", "research"],
        )
        body = r.json()
        assert body["title"] == "Write release notes"
        assert body["status"] == "todo"
        assert body["tags"] == ["frontend", "research"]
        assert body["id"]
        assert body["created_at"] == body["updated_at"]

    @allure.title("Get task by id returns same payload")
    def test_get_task(self, api_manager):
        created = api_manager.tasks.create(title="Triage flaky e2e").json()
        fetched = api_manager.tasks.get(created["id"]).json()
        assert fetched == created

    @allure.title("Patch updates only provided fields and bumps updated_at")
    @pytest.mark.smoke
    def test_patch_partial(self, api_manager):
        created = api_manager.tasks.create(
            title="Old title",
            description="keep me",
            tags=["bug"],
        ).json()
        patched = api_manager.tasks.patch(
            created["id"],
            status="in_progress",
        ).json()
        assert patched["status"] == "in_progress"
        assert patched["description"] == "keep me"
        assert patched["tags"] == ["bug"]
        assert patched["updated_at"] >= created["updated_at"]

    @allure.title("Patch tags is set-semantics (dedup + sort)")
    def test_patch_tags_dedup(self, api_manager):
        created = api_manager.tasks.create(title="Sort my tags").json()
        patched = api_manager.tasks.patch(
            created["id"],
            tags=["bug", "frontend", "frontend"],
        ).json()
        assert patched["tags"] == ["bug", "frontend"]

    @allure.title("Delete task -> 204, subsequent GET is 404")
    def test_delete_task(self, api_manager):
        created = api_manager.tasks.create(title="Temporary").json()
        api_manager.tasks.delete(created["id"])
        api_manager.tasks.get(created["id"], expected_status=404)

    @allure.title("GET non-existing id returns 404")
    @pytest.mark.negative
    def test_get_missing_returns_404(self, api_manager):
        api_manager.tasks.get("does-not-exist", expected_status=404)
