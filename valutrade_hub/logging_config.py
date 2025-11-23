from .infra.settings import SettingsLoader

settings = SettingsLoader("data/config.json")


class LoggingConfig:
    def __init__(self):
        self.log_path = settings.log_path
        self.format = settings.log_format
        self.level = settings.log_level
        self.rotation = settings.log_rotation_size
        self.mask_keywords = settings.mask_keywords
