import logging
import os
from datetime import datetime
from pathlib import Path
from threading import RLock
from typing import Optional

import pytz

from app import config


class TzFormatter(logging.Formatter) :
    """支持自定义时区的时间格式化"""

    def __init__(self, fmt: str, datefmt: str, tz) :
        super().__init__(fmt = fmt, datefmt = datefmt)
        self.tz = tz

    def formatTime(self, record, datefmt = None) :
        dt = datetime.fromtimestamp(record.created, self.tz)
        if datefmt :
            return dt.strftime(datefmt)
        return dt.isoformat()


class CustomLogger :
    def __init__(
            self,
            name: str = __name__,
            log_dir: str | os.PathLike = "log",
            timezone: str = "UTC",
            level: int = logging.DEBUG,
            console: bool = True,  # 是否输出到控制台
            console_level: Optional[int] = None,
    ) :
        self.name = name
        self._tz = pytz.timezone(timezone)
        self._lock = RLock()
        self._log_dir = Path(log_dir)
        self._log_dir.mkdir(parents = True, exist_ok = True)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = False  # 不向上级传播，避免重复

        # 统一的 formatter（文件与控制台可不同，也可以分开）
        self._fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        self._datefmt = "%Y-%m-%d %H:%M:%S"
        self._formatter = TzFormatter(self._fmt, self._datefmt, tz = self._tz)

        # 只添加一次 console handler
        if console :
            self._ensure_console_handler(level if console_level is None else console_level)

        # 初始化文件 handler
        self._current_date = None  # "YYYY-MM-DD"
        self._file_handler: Optional[logging.FileHandler] = None
        self._ensure_file_handler()

    # ---------- public API ----------
    def set_level(self, level: int) :
        self.logger.setLevel(level)

    def debug(self, msg, *args, **kwargs) :
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs) :
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs) :
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs) :
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs) :
        self.logger.critical(msg, *args, **kwargs)

    def check_or_update_file_handler(self) :
        """兼容你原来的调用点：每次 log 前可以调用它保证切日"""
        self._ensure_file_handler()

    # ---------- internals ----------
    def _ensure_console_handler(self, level: int) :
        with self._lock :
            for h in self.logger.handlers :
                if isinstance(h, logging.StreamHandler) :
                    return  # 已有，不重复加
            ch = logging.StreamHandler()
            ch.setLevel(level)
            ch.setFormatter(self._formatter)
            self.logger.addHandler(ch)

    def _ensure_file_handler(self) :
        with self._lock :
            today = datetime.now(self._tz).strftime("%Y-%m-%d")
            if self._current_date == today and self._file_handler :
                return

            # 生成目录 log/YYYY-MM/YYYY-MM-DD.log
            month_dir = self._log_dir / today[:7]
            month_dir.mkdir(parents = True, exist_ok = True)
            log_file = month_dir / f"{today}.log"

            # 替换文件 handler（只动文件 handler，不动其它）
            new_fh = logging.FileHandler(log_file, encoding = "utf-8")
            new_fh.setFormatter(self._formatter)

            # 先移除旧文件 handler
            if self._file_handler :
                try :
                    self.logger.removeHandler(self._file_handler)
                    self._file_handler.close()
                except Exception :
                    pass

            self.logger.addHandler(new_fh)
            self._file_handler = new_fh
            self._current_date = today


def set_up_logger(logger_name: str, loglevel: int = logging.DEBUG) -> CustomLogger :
    """
    生成特定的 logger（保持你的对外接口）
    """
    tz = config.get_config("timezone") or "UTC"
    return CustomLogger(logger_name, "log", tz, loglevel)
