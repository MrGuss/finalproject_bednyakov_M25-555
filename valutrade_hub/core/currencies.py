from abc import ABC, abstractmethod
from .exceptions import CurrencyNotFoundError
from ..infra.settings import SettingsLoader

settings = SettingsLoader("data/config.json")


class Currency(ABC):
    @abstractmethod
    def __init__(self, name: str, code: str):
        self._name = name
        self._code = code

    @abstractmethod
    def get_display_info(self) -> str:
        pass

    @property
    def name(self):
        return self._name

    @property
    def code(self):
        return self._code


class FiatCurrency(Currency):
    def __init__(self, name: str, code: str, issuing_country: str):
        super().__init__(name, code)
        self._issuing_country = issuing_country

    def get_display_info(self) -> str:
        return f"[FIAT] {self._code} - {self._name} (Issuing: {self._issuing_country})"


class CryptoCurrency(Currency):
    def __init__(self, name: str, code: str, algorithm: str, market_cap: float):
        super().__init__(name, code)
        self._algorithm = algorithm
        self._market_cap = market_cap

    def get_display_info(self) -> str:
        return f"[CRYPTO] {self._code} - {self._name} (Algorithm: {self._algorithm}, MCAP: {self._market_cap})"


CURRENCIES = {
    "EUR": FiatCurrency("Euro", "EUR", "Europe"),
    "USD": FiatCurrency("Dollar", "USD", "America"),
    "BTC": CryptoCurrency("Bitcoin", "BTC", "SHA256", 1.0),
}


def get_currency(code: str | None) -> Currency:
    if code is None:
        code = settings.default_base_currency

    if code.upper() in CURRENCIES:  # type: ignore
        return CURRENCIES[code.upper()]  # type: ignore
    else:
        raise CurrencyNotFoundError(code.upper())  # type: ignore
