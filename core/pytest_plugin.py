from pathlib import Path

import pytest

from core.browser import BrowserSession
from core.config import settings
from core.logger import attach_memory_handler, detach_memory_handler, get_logger, setup_logging
from core.reporting import attach_page_state, attach_screenshot, attach_text, write_environment

log = get_logger("run")


def pytest_configure(config):
    setup_logging()
    results_dir = config.getoption("--alluredir", default=None)
    if results_dir:
        write_environment(Path(results_dir))


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)
    if report.failed and report.when in ("setup", "call"):
        pw_page = item.funcargs.get("ui_page") if hasattr(item, "funcargs") else None
        log.error("Тест упал на этапе %s: %s", report.when, item.name)
        if pw_page is None:
            attach_text("Причина отсутствия скриншота", "Страница браузера не была создана")
        else:
            attach_page_state(pw_page)
            attach_screenshot(pw_page)


@pytest.fixture(scope="session")
def browser_session():
    session = BrowserSession(settings).start()
    yield session
    session.stop()


@pytest.fixture
def ui_page(request, browser_session):
    log.info("===== Старт: %s =====", request.node.name)
    memory = attach_memory_handler()
    context = browser_session.new_context()
    pw_page = context.new_page()
    yield pw_page
    call_report = getattr(request.node, "rep_call", None)
    setup_report = getattr(request.node, "rep_setup", None)
    failed = any(r is not None and r.failed for r in (setup_report, call_report))
    log.info("===== Конец: %s (%s) =====", request.node.name, "FAILED" if failed else "OK")
    context.close()
    attach_text("Лог теста", memory.text())
    detach_memory_handler(memory)
