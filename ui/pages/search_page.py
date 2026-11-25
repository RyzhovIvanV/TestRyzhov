import re

import allure

from ui.base_element import BaseElement
from ui.base_page import BasePage

ITEM = "div.search-result div.search-item"


class SearchResultsPage(BasePage):
    path = "/search/"
    title = "Результаты поиска"

    def __init__(self, page):
        super().__init__(page)
        self.items = BaseElement(page, ITEM, "Результаты поиска")
        self.item_titles = BaseElement(page, f"{ITEM} div.description a span", "Названия товаров в результатах")
        self.item_prices = BaseElement(page, f"{ITEM} div.price span", "Цены товаров в результатах")
        self.found_counter = BaseElement(
            page, "xpath=//*[starts-with(normalize-space(text()), 'Найдено:')]", "Счётчик «Найдено»"
        )

    def found_count(self) -> int:
        match = re.search(r"Найдено:\s*(\d+)", self.found_counter.text())
        return int(match.group(1)) if match else 0

    def result_link(self, title_part: str) -> BaseElement:
        xpath = (
            "xpath=//div[contains(@class,'search-item')]//div[@class='description']"
            f"/a[span[contains(normalize-space(.), {self._xpath_literal(title_part)})]]"
        )
        return BaseElement(self.page, xpath, f"Ссылка на товар «{title_part}»")

    def price_of(self, title_part: str) -> int:
        xpath = (
            f"xpath=//div[contains(@class,'search-item')][.//span[contains(normalize-space(.), "
            f"{self._xpath_literal(title_part)})]]//div[@class='price']/span"
        )
        return self.to_rubles(BaseElement(self.page, xpath, "Цена товара в результатах").text())

    def open_product(self, title_part: str) -> None:
        with allure.step(f"Открыть карточку товара «{title_part}» из результатов поиска"):
            self.result_link(title_part).click()
            self.page.wait_for_load_state("domcontentloaded")

    @staticmethod
    def _xpath_literal(value: str) -> str:
        if '"' not in value:
            return f'"{value}"'
        if "'" not in value:
            return f"'{value}'"
        parts = value.split('"')
        return "concat(" + ", '\"', ".join(f'"{p}"' for p in parts) + ")"
