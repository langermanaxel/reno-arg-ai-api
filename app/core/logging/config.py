"""Configuraciones de logging por entorno."""

import sys
from pathlib import Path
from typing import Dict, Any

LOGGING_CONFIGS: Dict[str, Dict[str, Any]] = {
    "development": {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "colored": {"()": "app.core.logging.setup.RichFormatter", "use_color": True}
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "colored",
                "stream": sys.stdout
            }
        },
        "loggers": {
            "app": {"level": "DEBUG", "handlers": ["console"], "propagate": False},
            "uvicorn": {"level": "INFO", "handlers": ["console"], "propagate": False}
        },
        "root": {"level": "INFO", "handlers": ["console"]}
    },
    "production": {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(name)s %(levelname)s %(message)s"
            }
        },
        "handlers": {
            "console": {"class": "logging.StreamHandler", "level": "INFO", "formatter": "json"},
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "json",
                "filename": "logs/app.log",
                "maxBytes": 10485760,
                "backupCount": 5,
                "encoding": "utf8"
            }
        },
        "loggers": {"app": {"level": "INFO", "handlers": ["console", "file"], "propagate": False}},
        "root": {"level": "WARNING", "handlers": ["console"]}
    }
}
