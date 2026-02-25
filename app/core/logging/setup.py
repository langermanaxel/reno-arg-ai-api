"""Setup y formatters de logging."""

import logging
from logging.config import dictConfig
from pathlib import Path
import sys
from .config import LOGGING_CONFIGS
from app.core.settings.base import settings

class RichFormatter(logging.Formatter):
    """Colores para desarrollo."""
    COLORS = {
        'DEBUG': '\033[36m', 'INFO': '\033[32m', 'WARNING': '\033[33m',
        'ERROR': '\033[31m', 'CRITICAL': '\033[35m', 'RESET': '\033[0m'
    }
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)

def setup_logging(override_env: str = None):
    """Configura logging por entorno."""
    env = override_env or settings.ENV
    
    # Limpieza
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.root.setLevel(logging.NOTSET)
    
    # Config
    config = LOGGING_CONFIGS.get(env, LOGGING_CONFIGS["development"])
    if env == "production":
        Path("logs").mkdir(exist_ok=True)
    
    dictConfig(config)
    logger = logging.getLogger("app")
    logger.info(f"🚀 Logging para {env.upper()}")
    return logger

def get_logger(name: str = "app") -> logging.Logger:
    return logging.getLogger(f"app.{name}")
