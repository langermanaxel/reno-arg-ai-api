"""Setup y formatters de logging."""

import logging
from logging.config import dictConfig
from pathlib import Path
import sys
import copy
from .config import LOGGING_CONFIGS


class RichFormatter(logging.Formatter):
    """Colores para desarrollo."""
    
    COLORS = {
        'DEBUG': '\033[36m',
        'INFO': '\033[32m',
        'WARNING': '\033[33m',
        'ERROR': '\033[31m',
        'CRITICAL': '\033[35m',
        'RESET': '\033[0m'
    }

    def __init__(self, fmt=None, datefmt=None, style='%', validate=True, use_color=True):
        super().__init__(fmt=fmt, datefmt=datefmt, style=style, validate=validate)
        self.use_color = use_color

    def format(self, record):
        record_copy = copy.copy(record)
        if self.use_color:
            color = self.COLORS.get(record_copy.levelname, self.COLORS['RESET'])
            record_copy.levelname = f"{color}{record_copy.levelname}{self.COLORS['RESET']}"
        return super().format(record_copy)


def setup_logging(override_env: str = None):
    """Configura logging por entorno."""
    from app.core.settings.base import settings  # ✅ import lazy, rompe el ciclo

    env = override_env or settings.ENV
    
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.root.setLevel(logging.NOTSET)
    
    config = LOGGING_CONFIGS.get(env, LOGGING_CONFIGS["development"])
    
    if env == "production":
        Path("logs").mkdir(exist_ok=True)
    
    try:
        dictConfig(config)
    except Exception as e:
        logging.basicConfig(level=logging.INFO)
        print(f"⚠️ Error configurando logging: {e}. Usando configuración básica.")
    
    logger = logging.getLogger("app")
    logger.info(f"🚀 Logging para {env.upper()}")
    return logger


def get_logger(name: str = "app") -> logging.Logger:
    """Retorna un logger hijo del logger principal."""
    return logging.getLogger(f"app.{name}")