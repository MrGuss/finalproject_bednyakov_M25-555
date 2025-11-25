from abc import ABC, abstractmethod
from .exceptions import CurrencyNotFoundError, ApiRequestError
from ..infra.settings import SettingsLoader
import json


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


def get_currencies() -> dict:
    currencies = {}
    er = get_exchange_rates()
    try:
        for rate in er["pairs"]:
            currencies[rate.split("_")[0]] = (
                FiatCurrency(rate.split("_")[0], rate.split("_")[0], "Unknown")
                if er["pairs"][rate]["source"] == "exchange_rates"
                else CryptoCurrency(rate.split("_")[0], rate.split("_")[0], "Unknown", -1)
            )
    except KeyError as e:
        raise ApiRequestError(f"Курс для {e} не найден в кеше.")
    return currencies


def get_currency(code: str | None) -> Currency:
    currencies = get_currencies()
    if code is None:
        code = settings.default_base_currency

    if code.upper() in currencies:  # type: ignore
        return currencies[code.upper()]  # type: ignore
    else:
        raise CurrencyNotFoundError(code.upper())  # type: ignore


def get_exchange_rates() -> dict:
    try:
        with open(f"{settings.data_path}/rates.json", "r") as f:
            exchange_rates = json.load(f)
        return exchange_rates
    except FileNotFoundError:
        raise ValueError("Локальный кеш курсов пуст. Выполните 'update_rates', чтобы загрузить данные.")
    except json.decoder.JSONDecodeError:
        raise ValueError("Локальный кеш курсов пуст. Выполните 'update_rates', чтобы загрузить данные.")


def get_cur_rate(currency: str, base: str | None = None) -> dict:
    exchange_rates = get_exchange_rates()
    try:
        return {
            "rate": exchange(currency, base or settings.default_base_currency, 1),
            "updated_at": exchange_rates["pairs"][
                f"{currency}_{settings.default_base_currency}"
            ]["updated_at"],
        }
    except KeyError as e:
        raise ValueError(f"Курс для {e} не найден в кеше.")


def exchange(from_currency: str, to_currency: str, amount: float) -> float:
    exchange_rates = get_exchange_rates()
    return (
        amount
        * exchange_rates["pairs"][f"{from_currency}_{settings.default_base_currency}"][
            "rate"
        ]
        / exchange_rates["pairs"][f"{to_currency}_{settings.default_base_currency}"][
            "rate"
        ]
    )
