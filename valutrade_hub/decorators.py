from datetime import datetime
import json
from .logging_config import LoggingConfig
import os

config = LoggingConfig()


def log_action(func):
    def wrapper(*args, **kwargs):
        print(args, kwargs)
        timestamp = datetime.now().isoformat()
        action = func.__name__.upper()
        username = kwargs.get('username') or kwargs.get('user_id')
        currency_code = kwargs.get('currency')
        amount = kwargs.get('amount')
        rate = kwargs.get('rate')
        base = kwargs.get('base')
        log_format = config.format
        try:
            func(*args, **kwargs)
            result_str = 'OK'
        except Exception as e:
            result_str = 'ERROR'
            if log_format == 'json':
                error_type = type(e).__name__
                error_message = str(e)
                log_record = {
                    'level': 'ERROR',
                    'timestamp': timestamp,
                    'action': action,
                    'username': username,
                    'currency_code': currency_code,
                    'amount': amount,
                    'rate': rate,
                    'base': base,
                    'result': result_str,
                    'error_type': error_type,
                    'error_message': error_message,
                }
            else:
                log_record = "ERROR {} {} {} {} {} {} {} {} {} {}".format(
                    timestamp, action, username, currency_code, amount, rate, base, result_str, error_type, error_message
                )

        log_record = None
        error_type = None
        error_message = None
        if result_str == 'OK':
            if log_format == 'json':
                log_record = {
                    'level': 'INFO',
                    'timestamp': timestamp,
                    'action': action,
                    'username': username,
                    'currency_code': currency_code,
                    'amount': amount,
                    'rate': rate,
                    'base': base,
                    'result': result_str,
                }
                if 
            else:
                log_record = f"INFO {timestamp} {action} {username} {currency_code} {amount} {rate} {base} {result_str}"
        if result_str == 'ERROR':
        if log_format == 'json':
            try:
                file_size_bytes = os.path.getsize(f"{config.log_path}/log.json")
            except FileNotFoundError:
                file_size_bytes = 0
            if file_size_bytes > config.rotation and config.rotation != 0:
                os.remove(f"{config.log_path}/log.json")
            with open(f"{config.log_path}/log.json", "a") as f:
                json.dump(log_record, f)
        else:
            print(log_record)
    return wrapper
