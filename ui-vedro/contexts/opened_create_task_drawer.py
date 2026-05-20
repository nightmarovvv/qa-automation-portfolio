import vedro

from interfaces.web.pages.board import BoardPage


@vedro.context
async def opened_create_task_drawer(board: BoardPage) -> None:
    """Click "New task" and wait until the drawer is interactive.

    Asserting on a specific input is more reliable than asserting on the
    drawer container — the drawer toggles `hidden`, but the inputs only
    become focusable once the form is mounted.
    """
    await board.header.create_task_button.click()
    await board.task_drawer.title_input.wait_for()
    await board.task_drawer.save_button.wait_for()
