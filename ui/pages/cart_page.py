import allure
from playwright.sync_api import expect

from core.logger import get_logger
from ui.base_element import BaseElement
from ui.base_page import BasePage

log = get_logger("cart")

ROW = "#basket_items_list div.cart-item"


class CartPage(BasePage):
    path = "/cart/"
    title = "Корзина"

    def __init__(self, page):
        super().__init__(page)
        self.rows = BaseElement(page, ROW, "Строки корзины")
        self.total = BaseElement(page, "#basket_form div.summary", "Итого")
        self.checkout_button = BaseElement(page, "#basket_form a.checkout", "Оформить заказ")

    def row(self, index: int = 0) -> "CartRow":
        return CartRow(self.page, self.rows.nth(index))

    def total_value(self) -> int:
        return self.to_rubles(self.total.text().replace("Итого:", ""))

    def clear(self) -> None:
        with allure.step("Очистить корзину"):
            count = self.rows.count()
            log.info("Позиций в корзине перед очисткой: %s", count)
            while count:
                self.row(0).delete_button.click()
                count -= 1
                expect(self.rows.locator).to_have_count(count)

    def checkout(self) -> None:
        with allure.step("Перейти к оформлению заказа"):
            self.checkout_button.click()
            self.page.wait_for_url("**/personal/order/make/**")


class CartRow:
    def __init__(self, page, root):
        self.root = root
        self.name = BaseElement(page, "div.cart-column-name a", "Название в корзине", parent=root)
        self.props = BaseElement(page, "div.cart-column-name-props", "Вариант товара в корзине", parent=root)
        self.price = BaseElement(page, "div.cart-column-price div.cart-column-value", "Цена в корзине", parent=root)
        self.quantity = BaseElement(page, "input[name^='QUANTITY_']", "Количество в корзине", parent=root)
        self.delete_button = BaseElement(page, "a.cart-delete-item", "Удалить из корзины", parent=root)

    def price_value(self) -> int:
        return BasePage.to_rubles(self.price.text())

    def quantity_value(self) -> int:
        return int(self.quantity.value())
