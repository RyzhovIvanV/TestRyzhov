import allure
from playwright.sync_api import Page, expect

from core.models import Customer, Product
from ui.pages.cart_page import CartPage
from ui.pages.checkout_page import CheckoutPage
from ui.pages.product_page import ProductPage
from ui.pages.search_page import SearchResultsPage


class ShopSteps:
    def __init__(self, page: Page):
        self.page = page
        self.cart = CartPage(page)
        self.search = SearchResultsPage(page)
        self.product = ProductPage(page)
        self.checkout = CheckoutPage(page)

    def ensure_empty_cart(self) -> None:
        with allure.step("Предусловие: корзина пользователя пуста"):
            self.cart.open()
            self.cart.clear()
            expect(self.cart.rows.locator).to_have_count(0)

    def search_product(self, product: Product) -> None:
        with allure.step(f"Шаг 2. Поиск «{product.search_query}»"):
            self.search.header.search(product.search_query)
            expect(self.search.items.locator.first).to_be_visible()
            assert self.search.found_count() > 0, "Счётчик «Найдено» равен 0"
            words = product.search_query.lower().split()
            titles = self.search.item_titles.texts()
            mismatched = [t for t in titles if not all(w in t.lower() for w in words)]
            assert not mismatched, f"Результаты не соответствуют запросу: {mismatched}"
            expect(self.search.result_link(product.title).locator).to_be_visible()
            assert self.search.price_of(product.title) == product.price, "Цена в результатах отличается от ожидаемой"

    def verify_product_card(self, product: Product) -> None:
        with allure.step("Шаг 3. Проверка карточки товара"):
            self.search.open_product(product.title)
            self.product.wait_loaded()
            assert product.url_part in self.page.url, "Открыта карточка другого товара"
            expect(self.product.heading.locator).to_have_text(product.title, ignore_case=True)
            assert self.product.price_value() == product.price, "Цена в карточке отличается от ожидаемой"
            expect(self.product.selected_color.locator).to_have_text(product.color)
            expect(self.product.add_to_cart_button.locator).to_be_visible()
            expect(self.product.add_to_cart_button.locator).to_be_enabled()

    def add_to_cart_and_verify(self, product: Product) -> None:
        with allure.step("Шаг 4. Добавление в корзину и проверка корзины"):
            self.product.add_to_cart()
            expect(self.product.header.basket_counter.locator).to_contain_text(str(product.quantity))
            self.product.go_to_cart()
            expect(self.cart.rows.locator).to_have_count(1)
            row = self.cart.row(0)
            expect(row.name.locator).to_have_text(product.title)
            expect(row.props.locator).to_contain_text(product.color)
            assert row.quantity_value() == product.quantity, "Неверное количество в корзине"
            assert row.price_value() == product.price, "Неверная цена в корзине"
            assert self.cart.total_value() == product.price * product.quantity, "Неверная сумма корзины"

    def fill_checkout(self, product: Product, customer: Customer) -> None:
        with allure.step("Шаг 5. Оформление заказа"):
            self.cart.checkout()
            self.checkout.wait_loaded()
            expect(self.checkout.basket_section.locator).to_contain_text(product.title)
            expect(self.checkout.basket_section.locator).to_contain_text(product.color)
            self.checkout.confirm_basket()
            self.checkout.choose_payment(customer.payment)
            self.checkout.fill_customer(customer)
            expect(self.checkout.field_errors.locator, "Есть ошибки в данных покупателя").to_have_count(0)
            assert self.checkout.total_value() == product.price * product.quantity, "Неверная итоговая сумма заказа"
            expect(self.checkout.submit_button.locator).to_be_visible()
            expect(self.checkout.submit_button.locator).to_be_enabled()

    def submit_and_verify_order(self, product: Product) -> str:
        with allure.step("Шаг 6. Отправка заказа и проверка подтверждения"):
            self.checkout.submit()
            number = self.checkout.order_number()
            assert number, "Не получен номер заказа"
            expect(self.checkout.confirmation.locator.first).to_be_visible()
            expect(self.page.locator("body")).to_contain_text(number)
            allure.dynamic.parameter("Номер заказа", number)
            return number
