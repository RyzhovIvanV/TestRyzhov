import os
from dataclasses import dataclass
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent

load_dotenv(ROOT / ".env")


def _as_bool(value) -> bool:
    return str(value).strip().lower() in ("1", "true", "yes", "on")


@dataclass(frozen=True)
class Settings:
    base_url: str
    browser: str
    headless: bool
    slow_mo_ms: int
    default_timeout_ms: int
    navigation_timeout_ms: int
    expect_timeout_ms: int
    optional_timeout_ms: int
    viewport_width: int
    viewport_height: int
    locale: str
    data_dir: Path
    log_level: str
    log_dir: Path
    user_login: str
    user_email: str
    user_password: str
    email_login_enabled: bool
    allow_order_submit: bool


def load_settings() -> Settings:
    cfg = yaml.safe_load((ROOT / "config" / "settings.yaml").read_text(encoding="utf-8"))
    env = os.environ.get
    timeouts = cfg["timeouts"]
    return Settings(
        base_url=env("BASE_URL", cfg["base_url"]).rstrip("/"),
        browser=env("BROWSER", cfg["browser"]),
        headless=_as_bool(env("HEADLESS", cfg["headless"])),
        slow_mo_ms=int(env("SLOW_MO_MS", cfg["slow_mo_ms"])),
        default_timeout_ms=int(env("TIMEOUT_MS", timeouts["default_ms"])),
        navigation_timeout_ms=int(env("NAVIGATION_TIMEOUT_MS", timeouts["navigation_ms"])),
        expect_timeout_ms=int(env("EXPECT_TIMEOUT_MS", timeouts["expect_ms"])),
        optional_timeout_ms=int(env("OPTIONAL_TIMEOUT_MS", timeouts["optional_ms"])),
        viewport_width=int(cfg["viewport"]["width"]),
        viewport_height=int(cfg["viewport"]["height"]),
        locale=cfg["locale"],
        data_dir=ROOT / env("DATA_DIR", cfg["data_dir"]),
        log_level=env("LOG_LEVEL", cfg["log"]["level"]).upper(),
        log_dir=ROOT / cfg["log"]["dir"],
        user_login=env("M1000_LOGIN", ""),
        user_email=env("M1000_EMAIL", ""),
        user_password=env("M1000_PASSWORD", ""),
        email_login_enabled=_as_bool(env("EMAIL_LOGIN_ENABLED", cfg["email_login_enabled"])),
        allow_order_submit=_as_bool(env("ALLOW_ORDER_SUBMIT", cfg["allow_order_submit"])),
    )


settings = load_settings()
