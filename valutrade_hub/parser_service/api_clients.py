from abc import ABC, abstractmethod
from .config import ParserConfig
from ..core.exceptions import ApiRequestError

import requests

config = ParserConfig()


class BaseApiClient(ABC):
    @abstractmethod
    def fetch_rates(self) -> dict:
        pass


class ExchangeratesApiClient(BaseApiClient):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = config.exchangerates_api_url
        self.url = "{exchangerates_api_url}/{api_key}/latest/{cur}"

    def fetch_rates(self) -> dict:
        url = self.url.format(exchangerates_api_url=self.api_url, api_key=self.api_key, cur=config.BASE_CURRENCY)
        response = requests.get(url)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            raise ApiRequestError("Failed to fetch rates")
        rates = response.json()["conversion_rates"]
        rates_parsed = {}
        for cur in config.FIAT_CURRENCIES:
            try:
                rates_parsed[f"{cur}_{config.BASE_CURRENCY}"] = rates[cur]
            except KeyError as e:
                raise ApiRequestError(f"Cant find currency {e} in response from Exchangerates")
        return rates_parsed


class CoinGeckoClient(BaseApiClient):
    def __init__(self) -> None:
        self.url = "{coingecko_api_url}/price?ids={ids}&vs_currencies={base_currency}"
        self.api_url = config.coingecko_api_url

    def fetch_rates(self) -> dict:
        url = self.url.format(
            coingecko_api_url=self.api_url,
            ids=",".join(config.CRYPTO_ID_MAP.values()),
            base_currency=config.BASE_CURRENCY,
        )
        response = requests.get(url)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            raise ApiRequestError("Failed to fetch rates")
        rates = response.json()
        rates_parsed = {}
        for k, v in config.CRYPTO_ID_MAP.items():
            try:
                rates_parsed[f"{k.upper()}_{config.BASE_CURRENCY}"] = rates[v][config.BASE_CURRENCY.lower()]
            except KeyError as e:
                raise ApiRequestError(f"Cant find currency {e} in response from CoinGecko")
        return rates_parsed
