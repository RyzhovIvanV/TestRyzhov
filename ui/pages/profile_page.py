from ui.base_element import BaseElement
from ui.base_page import BasePage


class ProfilePage(BasePage):
    path = "/personal/profile/"
    title = "Профиль пользователя"

    def __init__(self, page):
        super().__init__(page)
        self.login_field = BaseElement(page, "input[name='LOGIN']", "Логин в профиле", sensitive=True)
        self.email_field = BaseElement(page, "input[name='EMAIL']", "E-mail в профиле", sensitive=True)
        self.auth_form = BaseElement(page, "form[name='form_auth']", "Форма авторизации")
        self.content = BaseElement(page, "body", "Содержимое страницы")

    def identity_values(self) -> list[str]:
        values = []
        for field in (self.login_field, self.email_field):
            if field.count():
                values.append(field.value().strip().lower())
        return values

    def shows_user(self, login: str) -> bool:
        login = login.strip().lower()
        if login in self.identity_values():
            return True
        return login in self.content.text().lower()
