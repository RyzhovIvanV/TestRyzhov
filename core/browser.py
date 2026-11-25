from playwright.sync_api import Browser, BrowserContext, Playwright, expect, sync_playwright

from core.config import Settings
from core.logger import get_logger

log = get_logger("browser")


class BrowserSession:
    def __init__(self, cfg: Settings):
        self.cfg = cfg
        self._playwright: Playwright | None = None
        self.browser: Browser | None = None

    def start(self) -> "BrowserSession":
        log.info("Запуск браузера %s (headless=%s)", self.cfg.browser, self.cfg.headless)
        self._playwright = sync_playwright().start()
        browser_type = getattr(self._playwright, self.cfg.browser)
        self.browser = browser_type.launch(headless=self.cfg.headless, slow_mo=self.cfg.slow_mo_ms)
        expect.set_options(timeout=self.cfg.expect_timeout_ms)
        return self

    def new_context(self) -> BrowserContext:
        context = self.browser.new_context(
            base_url=self.cfg.base_url,
            viewport={"width": self.cfg.viewport_width, "height": self.cfg.viewport_height},
            locale=self.cfg.locale,
        )
        context.set_default_timeout(self.cfg.default_timeout_ms)
        context.set_default_navigation_timeout(self.cfg.navigation_timeout_ms)
        log.debug("Создан новый контекст браузера (чистые cookies и корзина гостя)")
        return context

    def stop(self) -> None:
        if self.browser:
            self.browser.close()
        if self._playwright:
            self._playwright.stop()
        log.info("Браузер остановлен")
