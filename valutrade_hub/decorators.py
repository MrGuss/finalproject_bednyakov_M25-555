import json
import os
from datetime import datetime

from .logging_config import LoggingConfig

config = LoggingConfig()


def log_action(func):
    def log_write(log_record, log_format):
        """
        Write log record to selected output
        :param log_record: log record
        :param log_format: log format
        :return: None
        """
        if log_format == "json":
            try:
                file_size_bytes = os.path.getsize(f"{config.log_path}/log.json")
            except FileNotFoundError:
                file_size_bytes = 0
            if file_size_bytes > config.rotation and config.rotation != 0:
                os.remove(f"{config.log_path}/log.json")
            with open(f"{config.log_path}/log.json", "a") as f:
                json.dump(log_record, f)
                f.write("\n")
        else:
            log_string = f'[{log_record["level"]}] ' + " ".join(
                [f"{k}={v}" for k, v in log_record.items() if k != "level"]
            )
            print(log_string)

    def wrapper(*args, **kwargs):
        """
        Wrapper for log_action
        :param args: args
        :param kwargs: kwargs
        :return: None
        """
        timestamp = datetime.now().isoformat()
        action = func.__name__.upper()
        log_format = config.format

        try:
            func(*args, **kwargs)
            log_record = {
                "level": "INFO",
                "timestamp": timestamp,
                "action": action,
            }
            log_record.update(kwargs)
            for keyword in config.mask_keywords:
                if keyword in log_record:
                    log_record[keyword] = "***"
            log_write(log_record, log_format)
        except Exception as e:
            error_type = type(e).__name__
            error_message = str(e)
            log_record = {
                "level": "ERROR",
                "timestamp": timestamp,
                "action": action,
                "error_type": error_type,
                "error_message": error_message,
            }
            log_record.update(kwargs)
            for keyword in config.mask_keywords:
                if keyword in log_record:
                    log_record[keyword] = "***"
            log_write(log_record, log_format)
            raise

    return wrapper
