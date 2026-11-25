import logging
import sys

from core.config import settings
from core.masking import mask

ROOT_LOGGER = "autotests"
FORMAT = "%(asctime)s | %(levelname)-5s | %(name)s | %(message)s"


class MaskingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = mask(record.getMessage())
        record.args = ()
        return True


class MemoryHandler(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.DEBUG)
        self.records: list[str] = []
        self.setFormatter(logging.Formatter(FORMAT))

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(self.format(record))

    def text(self) -> str:
        return "\n".join(self.records)


def setup_logging() -> logging.Logger:
    logging.addLevelName(logging.WARNING, "WARN")
    logger = logging.getLogger(ROOT_LOGGER)
    if logger.handlers:
        return logger
    logger.setLevel(getattr(logging, settings.log_level, logging.INFO))
    logger.propagate = False
    masking = MaskingFilter()
    formatter = logging.Formatter(FORMAT)

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    console.addFilter(masking)
    logger.addHandler(console)

    settings.log_dir.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(settings.log_dir / "run.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.addFilter(masking)
    logger.addHandler(file_handler)

    logger.addFilter(masking)
    return logger


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"{ROOT_LOGGER}.{name}")


def attach_memory_handler() -> MemoryHandler:
    handler = MemoryHandler()
    handler.addFilter(MaskingFilter())
    logging.getLogger(ROOT_LOGGER).addHandler(handler)
    return handler


def detach_memory_handler(handler: MemoryHandler) -> None:
    logging.getLogger(ROOT_LOGGER).removeHandler(handler)
