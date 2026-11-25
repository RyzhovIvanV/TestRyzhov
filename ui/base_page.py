import re

import allure
from playwright.sync_api import Page

from core.logger import get_logger
from ui.components.header import Header
from ui.components.hint_overlay import HintOverlay

log = get_logger("page")


class BasePage:
    path = "/"
    title = "Страница"

    def __init__(self, page: Page):
        self.page = page
        self.header = Header(page)
        HintOverlay(page).register()

    def open(self):
        with allure.step(f"Открыть страницу «{self.title}» ({self.path})"):
            log.info("Переход на %s", self.path)
            self.page.goto(self.path, wait_until="domcontentloaded")
            self.wait_loaded()
        return self

    def wait_loaded(self) -> None:
        self.page.wait_for_load_state("domcontentloaded")

    def user_id(self) -> str:
        script = "() => (window.BX && typeof BX.message === 'function' ? String(BX.message('USER_ID') || '') : '')"
        return self.page.evaluate(script).strip()

    def is_on(self, path_pattern: str) -> bool:
        return re.search(path_pattern, self.page.url) is not None

    @staticmethod
    def to_rubles(text: str) -> int:
        digits = re.sub(r"\D", "", text.split("руб")[0])
        return int(digits) if digits else 0
