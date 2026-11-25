import allure
from playwright.sync_api import expect

from ui.base_element import BaseElement
from ui.base_page import BasePage

BLOCK = "div.button-price-block"


class ProductPage(BasePage):
    title = "Карточка товара"

    def __init__(self, page):
        super().__init__(page)
        self.heading = BaseElement(page, "h1", "Название товара")
        self.price = BaseElement(page, f"{BLOCK} span.productPrice[itemprop='price']", "Цена товара")
        self.selected_color = BaseElement(
            page,
            "xpath=//div[contains(@class,'select-readycolor-item-pic') and contains(@class,'active')]"
            "/following-sibling::div[contains(@class,'select-readycolor-item-name')]",
            "Выбранный вариант (цвет)",
        )
        self.add_to_cart_button = BaseElement(
            page,
            "xpath=//div[contains(@class,'button-price-block')]"
            "//a[contains(@class,'zakaz_button') and normalize-space()='Добавить в корзину']",
            "Добавить в корзину",
        )
        self.go_to_cart_button = BaseElement(page, f"{BLOCK} a.zakaz_button.in_cart", "Перейти в корзину")

    def wait_loaded(self) -> None:
        self.heading.wait_visible()
        self.price.wait_visible()

    def price_value(self) -> int:
        content = self.price.attribute("content")
        return int(float(content)) if content else self.to_rubles(self.price.text())

    def add_to_cart(self) -> None:
        with allure.step("Добавить товар в корзину"):
            self.add_to_cart_button.click()
            expect(self.go_to_cart_button.locator).to_be_visible()

    def go_to_cart(self) -> None:
        with allure.step("Перейти в корзину из карточки товара"):
            self.go_to_cart_button.click()
            self.page.wait_for_url("**/cart/**")
