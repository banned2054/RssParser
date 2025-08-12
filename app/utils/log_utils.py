import logging
import os
from datetime import datetime

import pytz

from app import config

log_level_map = {
    "DEBUG"    : logging.DEBUG,
    "INFO"     : logging.INFO,
    "WARNING"  : logging.WARNING,
    "ERROR"    : logging.ERROR,
    "CRITICAL" : logging.CRITICAL,
}


class CustomLogger :
    def __init__(
            self, name = __name__, log_dir = "log", timezone = "UTC", level = logging.DEBUG
    ) :
        self.log_level = None
        self.name = name
        self.log_dir = log_dir
        self.timezone = pytz.timezone(timezone)
        self.logger = logging.getLogger(name)
        self.set_level(level)  # 设置日志等级

        if not os.path.exists(log_dir) :
            os.makedirs(log_dir)

        self.update_log_file()

    def update_log_file(self) :
        now = datetime.now(self.timezone)
        month_dir = now.strftime("%Y-%m")
        full_dir = os.path.join(self.log_dir, month_dir)

        if not os.path.exists(full_dir) :
            os.makedirs(full_dir)

        log_file = os.path.join(full_dir, now.strftime("%Y-%m-%d.log"))

        for handler in self.logger.handlers[:] :  # Remove all old handlers
            self.logger.removeHandler(handler)

        file_handler = logging.FileHandler(log_file, encoding = "utf-8")
        formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def set_level(self, level) :
        self.logger.setLevel(level)
        self.log_level = level

    def log(self, message, level) :
        self.check_or_update_file_handler()
        self.logger.log(level, message)
        if level >= self.log_level :
            print(message)

    def debug(self, message) :
        self.log(message, logging.DEBUG)

    def info(self, message) :
        self.log(message, logging.INFO)

    def warning(self, message) :
        self.log(message, logging.WARNING)

    def error(self, message) :
        self.log(message, logging.ERROR)

    def critical(self, message) :
        self.log(message, logging.CRITICAL)

    def check_or_update_file_handler(self) :
        now = datetime.now(self.timezone).strftime("%Y-%m-%d")
        for handler in self.logger.handlers :
            if isinstance(
                    handler, logging.FileHandler
            ) and not handler.baseFilename.endswith(f"{now}.log") :
                self.update_log_file()
                break


def set_up_logger(logger_name, loglevel = logging.DEBUG) :
    """
    生成特定的logger
    :return:
    """
    logger = CustomLogger(logger_name, "log", config.get_config("timezone"), loglevel)
    return logger
