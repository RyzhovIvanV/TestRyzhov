import allure

from core.logger import get_logger
from ui.base_element import BaseElement, ElementError
from ui.base_page import BasePage

log = get_logger("login")

FORM = "form[name='form_auth']"


class LoginPage(BasePage):
    path = "/auth/"
    title = "Авторизация"

    def __init__(self, page):
        super().__init__(page)
        self.form = BaseElement(page, FORM, "Форма авторизации")
        self.login_input = BaseElement(page, f"{FORM} input[name='USER_LOGIN']", "Логин", sensitive=True)
        self.password_input = BaseElement(page, f"{FORM} input[name='USER_PASSWORD']", "Пароль", sensitive=True)
        self.remember_checkbox = BaseElement(page, f"{FORM} #USER_REMEMBER", "Запомнить меня")
        self.submit_button = BaseElement(
            page, "xpath=//form[@name='form_auth']//input[@type='submit' and @name='Login']", "Войти"
        )
        self.error_message = BaseElement(page, "div.errortext", "Сообщение об ошибке авторизации")
        self.captcha = BaseElement(page, f"{FORM} input[name='captcha_word']", "CAPTCHA")

    def wait_loaded(self) -> None:
        self.form.wait_visible()

    def login(self, identifier: str, password: str) -> None:
        with allure.step("Заполнить и отправить форму авторизации"):
            self.login_input.fill(identifier)
            self.password_input.fill(password)
            with self.page.expect_navigation(wait_until="load"):
                self.submit_button.click()
            self.ensure_no_captcha()

    def ensure_no_captcha(self) -> None:
        if self.captcha.count() and self.captcha.is_visible():
            message = "На форме авторизации появилась CAPTCHA: автоматизация входа невозможна, сайт требует замены"
            log.error(message)
            raise ElementError(message)

    def error_text(self) -> str:
        return self.error_message.text() if self.error_message.count() else ""
