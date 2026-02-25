"""Setup y formatters de logging."""

import logging
from logging.config import dictConfig
from pathlib import Path
import sys
import copy  # Importante para no alterar el record original
from .config import LOGGING_CONFIGS
from app.core.settings.base import settings

class RichFormatter(logging.Formatter):
    """Colores para desarrollo."""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cian
        'INFO': '\033[32m',     # Verde
        'WARNING': '\033[33m',  # Amarillo
        'ERROR': '\033[31m',    # Rojo
        'CRITICAL': '\033[35m', # Púrpura
        'RESET': '\033[0m'
    }

    # FIX: Añadimos __init__ para capturar 'use_color' y evitar el TypeError
    def __init__(self, fmt=None, datefmt=None, style='%', validate=True, use_color=True):
        super().__init__(fmt=fmt, datefmt=datefmt, style=style, validate=validate)
        self.use_color = use_color

    def format(self, record):
        # Creamos una copia del record para no afectar a otros formatters (como el de archivo)
        record_copy = copy.copy(record)
        
        if self.use_color:
            color = self.COLORS.get(record_copy.levelname, self.COLORS['RESET'])
            record_copy.levelname = f"{color}{record_copy.levelname}{self.COLORS['RESET']}"
        
        return super().format(record_copy)

def setup_logging(override_env: str = None):
    """Configura logging por entorno."""
    env = override_env or settings.ENV
    
    # Limpieza de handlers existentes
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.root.setLevel(logging.NOTSET)
    
    # Obtener configuración del diccionario
    config = LOGGING_CONFIGS.get(env, LOGGING_CONFIGS["development"])
    
    if env == "production":
        Path("logs").mkdir(exist_ok=True)
    
    # Aplicar la configuración
    try:
        dictConfig(config)
    except Exception as e:
        # Fallback básico si falla la configuración compleja
        logging.basicConfig(level=logging.INFO)
        print(f"⚠️ Error configurando logging: {e}. Usando configuración básica.")
    
    logger = logging.getLogger("app")
    logger.info(f"🚀 Logging para {env.upper()}")
    return logger

def get_logger(name: str = "app") -> logging.Logger:
    """Retorna un logger hijo del logger principal."""
    return logging.getLogger(f"app.{name}")