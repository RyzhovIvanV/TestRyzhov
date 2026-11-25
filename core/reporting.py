import platform
from pathlib import Path

import allure
from playwright.sync_api import Page

from core.config import settings
from core.logger import get_logger
from core.masking import mask

log = get_logger("report")

SENSITIVE_SELECTORS = (
    "input[type='password']",
    "input[name='USER_LOGIN']",
    "input[name^='ORDER_PROP_']",
    "textarea[name^='ORDER_PROP_']",
    "div.lkkab",
    "input[name='LOGIN']",
    "input[name='EMAIL']",
)


def attach_text(name: str, text: str) -> None:
    allure.attach(mask(text), name=name, attachment_type=allure.attachment_type.TEXT)


def attach_screenshot(page: Page, name: str = "Скриншот при падении") -> None:
    try:
        masks = [page.locator(selector) for selector in SENSITIVE_SELECTORS]
        png = page.screenshot(full_page=False, mask=masks, timeout=settings.default_timeout_ms)
        allure.attach(png, name=name, attachment_type=allure.attachment_type.PNG)
    except Exception as error:
        reason = f"Скриншот недоступен: {type(error).__name__}: {error}"
        log.error(reason)
        attach_text("Причина отсутствия скриншота", reason)


def attach_page_state(page: Page) -> None:
    try:
        attach_text("URL при падении", page.url)
    except Exception as error:
        attach_text("URL при падении", f"недоступен: {error}")


def write_environment(results_dir: Path) -> None:
    results_dir.mkdir(parents=True, exist_ok=True)
    lines = {
        "Base.URL": settings.base_url,
        "Browser": settings.browser,
        "Headless": settings.headless,
        "Python": platform.python_version(),
        "OS": platform.platform(),
        "Email.Login": settings.email_login_enabled,
        "Order.Submit": settings.allow_order_submit,
    }
    content = "\n".join(f"{key}={value}" for key, value in lines.items())
    (results_dir / "environment.properties").write_text(content, encoding="utf-8")
