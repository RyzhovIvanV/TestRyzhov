from playwright.sync_api import Locator, Page

from core.logger import get_logger

log = get_logger("overlay")

_REGISTERED_ATTR = "_mebel1000_hint_handler"


class HintOverlay:
    NEXT_BUTTON = "div.enjoyhint .enjoyhint_next_btn"

    def __init__(self, page: Page):
        self.page = page

    def register(self) -> None:
        if getattr(self.page, _REGISTERED_ATTR, False):
            return
        self.page.add_locator_handler(self.page.locator(self.NEXT_BUTTON), self._dismiss)
        setattr(self.page, _REGISTERED_ATTR, True)

    @staticmethod
    def _dismiss(button: Locator) -> None:
        log.debug("Закрыта подсказка-оверлей «Понятно»")
        button.click()
