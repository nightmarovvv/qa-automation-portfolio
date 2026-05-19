import vedro

from interfaces.web.pages.board import BoardPage


@vedro.context
async def opened_edit_task_drawer(board: BoardPage, task_id: str) -> None:
    """Open the drawer in edit mode for a specific task id."""
    card = board.task_list.get_list_task_by_id(task_id)
    await card.wait_for()
    await card.click()
    await board.task_drawer.title_input.wait_for()
    await board.task_drawer.save_button.wait_for()
