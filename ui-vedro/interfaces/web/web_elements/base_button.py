from interfaces.web.web_elements.base_element import BaseElement
from interfaces.web.web_elements.mixins import Clickable, Readable


class BaseButton(BaseElement, Clickable, Readable):
    pass
