import re

from core.config import settings

MASK = "***"

_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
_PHONE = re.compile(r"\+?\d[\d\s()\-]{8,}\d")
_COOKIE = re.compile(r"(?i)(cookie|token|sessid|PHPSESSID)([\"'=:\s]+)[^\s;,\"']+")


def _secrets() -> list[str]:
    values = [settings.user_password, settings.user_email, settings.user_login]
    return sorted({v for v in values if v}, key=len, reverse=True)


def mask(text) -> str:
    result = str(text)
    for secret in _secrets():
        result = result.replace(secret, MASK)
    result = _EMAIL.sub(lambda m: m.group(0)[0] + MASK + "@" + MASK, result)
    result = _PHONE.sub("+7" + MASK, result)
    result = _COOKIE.sub(lambda m: m.group(1) + m.group(2) + MASK, result)
    return result


def mask_identifier(value: str) -> str:
    if not value:
        return "<пусто>"
    if value in _secrets():
        return MASK
    return mask(value)
