import allure
import pytest

from autotest.steps.auth_steps import AuthSteps
from autotest.steps.shop_steps import ShopSteps
from core.config import settings
from core.data import credentials_missing, load_order_scenarios
from core.logger import get_logger

log = get_logger("e2e")

SCENARIOS = load_order_scenarios()


def _describe(scenario, case_id: str, title: str):
    allure.dynamic.id(case_id)
    allure.dynamic.label("case_id", case_id)
    allure.dynamic.title(f"{case_id}. {title}")
    allure.dynamic.parameter("Запрос", scenario.product.search_query)
    allure.dynamic.parameter("Товар", scenario.product.title)
    allure.dynamic.parameter("Вариант", scenario.product.color)
    allure.dynamic.parameter("Цена", scenario.product.price)
    allure.dynamic.parameter("Оплата", scenario.customer.payment)


@pytest.fixture
def shopper(ui_page):
    missing = credentials_missing()
    if missing:
        pytest.skip(f"Не заданы переменные окружения: {missing}")
    shop = ShopSteps(ui_page)
    yield AuthSteps(ui_page), shop
    with allure.step("Постусловие: очистить корзину пользователя"):
        try:
            if shop.cart.user_id():
                shop.ensure_empty_cart()
        except AssertionError as error:
            log.warning("Не удалось очистить корзину после теста: %s", error)


def _login_and_prepare(auth: AuthSteps, shop: ShopSteps) -> None:
    with allure.step("Шаг 1. Вход"):
        auth.login_as_default_user()
    shop.ensure_empty_cart()


@allure.epic("mebel-1000.ru")
@allure.feature("Сквозной сценарий")
@allure.story("Покупка товара")
@pytest.mark.e2e
@pytest.mark.parametrize("scenario", SCENARIOS, ids=[s.case_id for s in SCENARIOS])
def test_checkout_until_submit(shopper, scenario):
    _describe(scenario, scenario.case_id, scenario.title)
    auth, shopper = shopper
    _login_and_prepare(auth, shopper)
    shopper.search_product(scenario.product)
    shopper.verify_product_card(scenario.product)
    shopper.add_to_cart_and_verify(scenario.product)
    shopper.fill_checkout(scenario.product, scenario.customer)
    with allure.step("Отправка заказа не выполняется: ALLOW_ORDER_SUBMIT=false"):
        pass


@allure.epic("mebel-1000.ru")
@allure.feature("Сквозной сценарий")
@allure.story("Создание заказа")
@pytest.mark.e2e
@pytest.mark.parametrize("scenario", SCENARIOS, ids=[f"{s.case_id}-SUBMIT" for s in SCENARIOS])
def test_order_created(shopper, scenario):
    case_id = f"{scenario.case_id}-SUBMIT"
    _describe(scenario, case_id, "Полный путь до создания заказа")
    if not settings.allow_order_submit:
        pytest.skip("Создание реальных заказов отключено (ALLOW_ORDER_SUBMIT=false)")
    auth, shop = shopper
    _login_and_prepare(auth, shop)
    shop.search_product(scenario.product)
    shop.verify_product_card(scenario.product)
    shop.add_to_cart_and_verify(scenario.product)
    shop.fill_checkout(scenario.product, scenario.customer)
    shop.submit_and_verify_order(scenario.product)
