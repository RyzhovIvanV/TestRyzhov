import re

import allure
from playwright.sync_api import Page

from ui.base_element import BaseElement


class Header:
    def __init__(self, page: Page):
        self.page = page
        self.account_block = BaseElement(page, "div.lkkab", "Блок личного кабинета")
        self.login_link = BaseElement(page, "div.lkkab a[href='/auth/']", "Ссылка «Вход»")
        self.register_link = BaseElement(page, "div.lkkab a[href='/auth/?register=yes']", "Ссылка «Регистрация»")
        self.search_input = BaseElement(page, "form[action='/search/'] input[name='q']", "Поле поиска")
        self.search_button = BaseElement(page, "form[action='/search/'] button.header_search_button", "Кнопка поиска")
        self.basket_counter = BaseElement(page, "a.header-basket-link .header-busket-count", "Счётчик корзины")

    def search(self, query: str) -> None:
        with allure.step(f"Выполнить поиск «{query}» через шапку сайта"):
            self.search_input.fill(query)
            self.search_input.press("Enter")
            self.page.wait_for_url(re.compile(r"/search/\?"))

    def basket_count(self) -> int:
        digits = re.sub(r"\D", "", self.basket_counter.text())
        return int(digits) if digits else 0
