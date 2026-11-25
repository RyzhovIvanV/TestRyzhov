import re

import allure
from playwright.sync_api import Page, expect

from core.config import settings
from ui.pages.login_page import LoginPage
from ui.pages.profile_page import ProfilePage


class AuthSteps:
    def __init__(self, page: Page):
        self.page = page
        self.login_page = LoginPage(page)

    def login(self, identifier: str, password: str) -> None:
        with allure.step("Авторизация пользователя"):
            self.login_page.open()
            self.login_page.login(identifier, password)

    def assert_logged_in_as(self, expected_login: str) -> None:
        with allure.step("Проверить успешную авторизацию и сессию нужного пользователя"):
            expect(self.login_page.form.locator, "Форма входа должна исчезнуть").to_be_hidden()
            expect(self.login_page.error_message.locator, "Сообщения об ошибке быть не должно").to_have_count(0)
            expect(self.login_page.header.login_link.locator, "Ссылка «Вход» должна исчезнуть").to_have_count(0)
            assert re.fullmatch(r"\d+", self.login_page.user_id()), "В сессии нет USER_ID авторизованного пользователя"
            profile = ProfilePage(self.page).open()
            expect(profile.auth_form.locator, "Профиль должен открываться без входа").to_have_count(0)
            assert profile.shows_user(expected_login), "Открыт профиль другого пользователя"

    def assert_login_rejected(self, expected_error: str) -> None:
        with allure.step(f"Проверить отказ во входе с ошибкой «{expected_error}»"):
            expect(self.login_page.error_message.locator).to_be_visible()
            expect(self.login_page.error_message.locator).to_have_text(re.compile(re.escape(expected_error)))
            expect(self.login_page.form.locator).to_be_visible()
            expect(self.login_page.header.login_link.locator).to_be_visible()
            assert self.login_page.user_id() == "", "Появилась авторизованная сессия после неудачного входа"

    def login_as_default_user(self) -> None:
        self.login(settings.user_login, settings.user_password)
        self.assert_logged_in_as(settings.user_login)
