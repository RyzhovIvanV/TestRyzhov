import allure
import pytest

from autotest.steps.auth_steps import AuthSteps
from core.config import settings
from core.data import credentials_missing, load_login_cases

CASES = load_login_cases()
POSITIVE = [c for c in CASES if c.is_positive]
NEGATIVE = [c for c in CASES if not c.is_positive]


def _describe(case):
    allure.dynamic.id(case.case_id)
    allure.dynamic.label("case_id", case.case_id)
    allure.dynamic.title(f"{case.case_id}. {case.title}")
    allure.dynamic.parameter("Вид идентификатора", case.kind)
    allure.dynamic.parameter("Идентификатор", case.safe_identifier)
    allure.dynamic.parameter("Пароль", case.safe_password)
    allure.dynamic.parameter("Ожидаемый результат", case.error or "успешный вход")


@pytest.fixture(autouse=True)
def _require_credentials():
    missing = credentials_missing()
    if missing:
        pytest.skip(f"Не заданы переменные окружения: {missing}")


@allure.epic("mebel-1000.ru")
@allure.feature("Авторизация")
@allure.story("Позитивные проверки")
@pytest.mark.auth
@pytest.mark.positive
@pytest.mark.parametrize("case", POSITIVE, ids=[c.case_id for c in POSITIVE])
def test_login_success(ui_page, case):
    _describe(case)
    steps = AuthSteps(ui_page)
    steps.login(case.identifier, case.password)
    steps.assert_logged_in_as(settings.user_login)


@allure.epic("mebel-1000.ru")
@allure.feature("Авторизация")
@allure.story("Негативные проверки")
@pytest.mark.auth
@pytest.mark.negative
@pytest.mark.parametrize("case", NEGATIVE, ids=[c.case_id for c in NEGATIVE])
def test_login_rejected(ui_page, case):
    _describe(case)
    allure.dynamic.tag(case.group)
    steps = AuthSteps(ui_page)
    steps.login(case.identifier, case.password)
    steps.assert_login_rejected(case.error)
