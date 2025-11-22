from typing import Any
import json


class SettingsLoader:
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        I use new because I dont know what is metaclass
        """
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.__init__(*args, **kwargs)
        return cls._instance

    def __init__(self, config_path):
        self.config_path = config_path
        with open(self.config_path, "r") as f:
            config = json.load(f)

        self.data_path = config["data_path"]
        self.rates_ttl_seconds = config["rates_ttl_seconds"]
        self.default_base_currency = config["default_base_currency"]
        self.log_path = config["log_path"]
        self.log_format = config["log_format"]
        self.log_level = config["log_level"]
        self.log_rotation_size = config["log_rotation_size"]

    def get(self, key: str, default: Any = None):
        try:
            return getattr(self, key)
        except AttributeError:
            return default
