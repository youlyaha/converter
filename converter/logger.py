"""Отдельный модуль журналирования приложения."""
import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "app.log"


def setup_logging() -> logging.Logger:
    """Настраивает запись журнала в UTF-8."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log = logging.getLogger("converter")
    log.setLevel(logging.INFO)
    log.propagate = False
    if not log.handlers:
        handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        ))
        log.addHandler(handler)
    return log


logger = setup_logging()
