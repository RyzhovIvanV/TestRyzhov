import json

from core.config import settings
from core.models import Customer, LoginCase, OrderScenario, Product


def _placeholders() -> dict[str, str]:
    return {
        "{LOGIN}": settings.user_login,
        "{EMAIL}": settings.user_email,
        "{PASSWORD}": settings.user_password,
    }


def _resolve(value: str) -> str:
    for key, real in _placeholders().items():
        value = value.replace(key, real)
    return value


def _read(name: str):
    return json.loads((settings.data_dir / name).read_text(encoding="utf-8"))


def load_login_cases() -> list[LoginCase]:
    cases = []
    for raw in _read("login_cases.json"):
        if raw["kind"] == "email" and not settings.email_login_enabled:
            continue
        cases.append(
            LoginCase(
                case_id=raw["id"],
                title=raw["title"],
                group=raw["group"],
                kind=raw["kind"],
                identifier=_resolve(raw["identifier"]),
                password=_resolve(raw["password"]),
                expected=raw["expected"],
                error=raw.get("error", ""),
            )
        )
    return cases


def load_order_scenarios() -> list[OrderScenario]:
    scenarios = []
    for raw in _read("order_scenarios.json"):
        scenarios.append(
            OrderScenario(
                case_id=raw["id"],
                title=raw["title"],
                product=Product(**raw["product"]),
                customer=Customer(**raw["customer"]),
            )
        )
    return scenarios


def credentials_missing() -> str:
    missing = [
        name
        for name, value in (
            ("M1000_LOGIN", settings.user_login),
            ("M1000_PASSWORD", settings.user_password),
        )
        if not value
    ]
    if settings.email_login_enabled and not settings.user_email:
        missing.append("M1000_EMAIL")
    return ", ".join(missing)
