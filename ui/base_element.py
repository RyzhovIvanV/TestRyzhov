from __future__ import annotations

import allure
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Locator, Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from core.config import settings
from core.logger import get_logger
from core.masking import mask

log = get_logger("element")


class ElementError(AssertionError):
    pass


class BaseElement:
    def __init__(self, page: Page, selector: str, name: str, sensitive: bool = False, parent: Locator | None = None):
        self.page = page
        self.selector = selector
        self.name = name
        self.sensitive = sensitive
        self._parent = parent

    @property
    def locator(self) -> Locator:
        root = self._parent if self._parent is not None else self.page
        return root.locator(self.selector)

    def _fail(self, action: str, error: Exception) -> ElementError:
        message = (
            f"Не удалось выполнить «{action}» для элемента «{self.name}». "
            f"Селектор: {self.selector}. URL: {self.page.url}. Причина: {str(error).splitlines()[0]}"
        )
        log.error(mask(message))
        return ElementError(mask(message))

    def _run(self, action: str, func):
        log.debug("%s: «%s» [%s]", action, self.name, self.selector)
        try:
            return func()
        except (PlaywrightTimeoutError, PlaywrightError) as error:
            raise self._fail(action, error) from None

    def wait_visible(self, timeout: int | None = None) -> BaseElement:
        self._run("ожидание видимости", lambda: self.locator.first.wait_for(state="visible", timeout=timeout))
        return self

    def wait_hidden(self, timeout: int | None = None) -> BaseElement:
        self._run("ожидание скрытия", lambda: self.locator.first.wait_for(state="hidden", timeout=timeout))
        return self

    def is_visible(self) -> bool:
        return self.locator.first.is_visible()

    def appears_within(self, timeout: int | None = None) -> bool:
        try:
            self.locator.first.wait_for(state="visible", timeout=timeout or settings.optional_timeout_ms)
            return True
        except PlaywrightTimeoutError:
            return False

    def click(self) -> None:
        with allure.step(f"Нажать «{self.name}»"):
            log.info("Нажатие: %s", self.name)
            self._run("клик", lambda: self.locator.first.click())

    def fill(self, value: str) -> None:
        shown = "***" if self.sensitive else (mask(value) if value else "<пусто>")
        with allure.step(f"Ввести в поле «{self.name}»: {shown}"):
            log.info("Ввод в поле «%s»: %s", self.name, shown)
            self._run("ввод текста", lambda: self.locator.first.fill(value))

    def press(self, key: str) -> None:
        with allure.step(f"Нажать клавишу {key} в «{self.name}»"):
            self._run(f"нажатие {key}", lambda: self.locator.first.press(key))

    def check(self) -> None:
        with allure.step(f"Отметить «{self.name}»"):
            self._run("отметка", lambda: self.locator.first.check())

    def text(self) -> str:
        return self._run("чтение текста", lambda: self.locator.first.inner_text()).strip()

    def texts(self) -> list[str]:
        return [t.strip() for t in self._run("чтение текстов", lambda: self.locator.all_inner_texts())]

    def value(self) -> str:
        return self._run("чтение значения", lambda: self.locator.first.input_value())

    def attribute(self, name: str) -> str | None:
        return self._run(f"чтение атрибута {name}", lambda: self.locator.first.get_attribute(name))

    def count(self) -> int:
        return self.locator.count()

    def nth(self, index: int) -> Locator:
        return self.locator.nth(index)
