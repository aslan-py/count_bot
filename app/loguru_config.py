"""Настройки логирования через Loguru.

Класс LoguruStart создается атрибутом экземпляра - пакеой для логов на один
    уровень выше корневой папки app.
_create_logs_folder - Создаем папку если её нет с названием logs.
start_loguru - запускает основные настройки логгера.
"""

import sys
from pathlib import Path

from loguru import logger

from app.constants import LoguruSetup


class LoguruStart:
    """Настройки логирования Loguru."""

    def __init__(self) -> None:
        """Создание папки для логов."""
        self.dir_base = Path(__file__).resolve().parent.parent

    def _create_logs_folder(self) -> Path:
        """Создает папку для логов."""
        logs_dir = self.dir_base / LoguruSetup.DIR_NAME
        logs_dir.mkdir(exist_ok=True)
        return logs_dir

    def start_loguru(self) -> None:
        """Основные настройки логгера."""
        logs_dir = self._create_logs_folder()
        logger.remove()

        logger.add(sink=sys.stderr, format=LoguruSetup.CONSOLE_FORMAT)
        logger.add(
            logs_dir / LoguruSetup.LOG_NAME,
            rotation=LoguruSetup.ROTATION,
            retention=LoguruSetup.RETENTION,
            level=LoguruSetup.LEVEL,
            format=LoguruSetup.LOG_FORMAT,
            encoding=LoguruSetup.ENCODING,
        )
