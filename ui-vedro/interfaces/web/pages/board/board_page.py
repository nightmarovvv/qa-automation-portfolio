from interfaces.web.pages.board.components.task_drawer import TaskDrawer
from interfaces.web.pages.board.components.task_list import TaskList
from interfaces.web.pages.page import BasePage
from interfaces.web.web_elements import BaseText


class BoardPage(BasePage):
    RELATIVE_URL = "/"

    @property
    def task_list(self) -> TaskList:
        return TaskList(self.raw)

    @property
    def task_drawer(self) -> TaskDrawer:
        return TaskDrawer(self.raw)

    @property
    def task_counter(self) -> BaseText:
        return BaseText(self.raw, data_test="task-counter")

    @property
    def loading_indicator(self) -> BaseText:
        return BaseText(self.raw, data_test="loading-indicator")

    @property
    def empty_state(self) -> BaseText:
        return BaseText(self.raw, data_test="empty-state")
