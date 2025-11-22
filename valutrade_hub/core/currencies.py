from abc import ABC, abstractmethod
from .exceptions import CurrencyNotFoundError


class Currency(ABC):
    @abstractmethod
    def __init__(self, name: str, code: float):
        self._name = name
        self._code = code

    @abstractmethod
    def get_display_info(self) -> str:
        pass


class FiatCurrency(Currency):
    def __init__(self, name: str, code: float, issuing_country: str):
        super().__init__(name, code)
        self._issuing_country = issuing_country

    def get_display_info(self) -> str:
        return f"[FIAT] {self._name} (Issuing: {self._issuing_country})"


class CryptoCurrency(Currency):
    def __init__(self, name: str, code: float, algorithm: str, market_cap: float):
        super().__init__(name, code)
        self._algorithm = algorithm
        self._market_cap = market_cap

    def get_display_info(self) -> str:
        return f"[CRYPTO] {self._name} (Algorithm: {self._algorithm}, MCAP: {self._market_cap})"


CURRENCIES = {
    "EUR": FiatCurrency("Euro", 1.0, "Europe"),
    "USD": FiatCurrency("Dollar", 1.0, "America"),
    "BTC": CryptoCurrency("Bitcoin", 1.0, "SHA256", 1.0),
}


def get_currency(code: str):
    if code in CURRENCIES:
        return CURRENCIES[code]
    else:
        raise CurrencyNotFoundError(code)
