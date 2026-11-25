import re

import allure
from playwright.sync_api import expect

from core.models import Customer
from ui.base_element import BaseElement
from ui.base_page import BasePage

BASKET = "bx-soa-basket"
PAYMENT = "bx-soa-paysystem"
PROPERTIES = "bx-soa-properties"


class CheckoutPage(BasePage):
    path = "/personal/order/make/"
    title = "Оформление заказа"

    def __init__(self, page):
        super().__init__(page)
        self.form = BaseElement(page, "form#bx-soa-order-form", "Форма оформления заказа")
        self.basket_section = BaseElement(page, f"#{BASKET}", "Раздел «Товары в заказе»")
        self.payment_section = BaseElement(page, f"#{PAYMENT}", "Раздел «Оплата»")
        self.properties_section = BaseElement(page, f"#{PROPERTIES}", "Раздел «Покупатель»")
        self.selected_payment = BaseElement(
            page, f"#{PAYMENT} div.bx-soa-pp-company.bx-selected", "Выбранный способ оплаты"
        )
        self.full_name = BaseElement(page, "[name='ORDER_PROP_1']", "Ф.И.О.", sensitive=True)
        self.email = BaseElement(page, "[name='ORDER_PROP_2']", "E-Mail", sensitive=True)
        self.phone = BaseElement(page, "[name='ORDER_PROP_3']", "Телефон", sensitive=True)
        self.address = BaseElement(page, "[name='ORDER_PROP_7']", "Адрес доставки", sensitive=True)
        self.field_errors = BaseElement(page, f"#{PROPERTIES} .form-group.has-error", "Ошибки полей покупателя")
        self.order_total = BaseElement(page, "#bx-soa-total", "Итог заказа")
        self.submit_button = BaseElement(page, "#bx-soa-orderSave a", "Оформить заказ")
        self.confirmation = BaseElement(
            page, "xpath=//*[contains(normalize-space(.), 'успешно создан') and not(*)]", "Подтверждение заказа"
        )

    def wait_loaded(self) -> None:
        self.form.wait_visible()
        self.basket_section.wait_visible()

    def _next_button(self, section_id: str) -> BaseElement:
        return BaseElement(
            self.page,
            f"xpath=//div[@id='{section_id}']//a[normalize-space()='Далее']",
            f"Далее ({section_id})",
        )

    def _section_selected(self, section_id: str):
        return expect(self.page.locator(f"#{section_id}")).to_have_class(re.compile(r"\bbx-selected\b"))

    def confirm_basket(self) -> None:
        with allure.step("Подтвердить состав заказа и перейти к оплате"):
            self._next_button(BASKET).click()
            self._section_selected(PAYMENT)

    def choose_payment(self, name: str) -> None:
        with allure.step(f"Выбрать способ оплаты «{name}»"):
            option = BaseElement(
                self.page,
                f"xpath=//div[@id='{PAYMENT}']//div[contains(@class,'bx-soa-pp-company') and contains(@class,'col-')]"
                f"[normalize-space()='{name}']",
                f"Способ оплаты «{name}»",
            )
            option.click()
            expect(self.selected_payment.locator).to_have_text(re.compile(rf"^\s*{re.escape(name)}\s*$"))
            self._next_button(PAYMENT).click()
            self._section_selected(PROPERTIES)

    def fill_customer(self, customer: Customer) -> None:
        with allure.step("Заполнить данные покупателя (тестовые)"):
            for field, value in (
                (self.full_name, customer.full_name),
                (self.email, customer.email),
                (self.phone, customer.phone),
                (self.address, customer.address),
            ):
                field.fill(value)
                field.press("Tab")

    def total_value(self) -> int:
        match = re.search(r"Итого:\s*([\d\s ]+)", self.order_total.text())
        return int(re.sub(r"\D", "", match.group(1))) if match else 0

    def submit(self) -> None:
        with allure.step("Отправить заказ"):
            self.submit_button.click()
            self.page.wait_for_url(re.compile(r"ORDER_ID=\d+"))

    def order_number(self) -> str:
        match = re.search(r"ORDER_ID=(\d+)", self.page.url)
        return match.group(1) if match else ""
