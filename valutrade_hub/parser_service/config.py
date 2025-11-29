from ..infra.settings import SettingsLoader

settings = SettingsLoader("data/config.json")


class ParserConfig:
    def __init__(self):
        self.coingecko_api_key = settings.coingeko_api_key
        self.exchangerates_api_key = settings.exchangerates_api_key
        self.coingecko_api_url = "https://api.coingecko.com/api/v3/simple/"
        self.exchangerates_api_url = "https://v6.exchangerate-api.com/v6"

        self.FIAT_CURRENCIES = ["USD", "EUR", "RUB", "CZK"]
        self.CRYPTO_CURRENCIES = ["BTC", "ETH", "XMR"]
        self.CRYPTO_ID_MAP = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "XMR": "monero",
        }

        self.BASE_CURRENCY = "USD"

        self.REQUEST_TIMEOUT = 10
        self.rates_path = "data/rates.json"
        self.exchange_path = "data/exchange_rates.json"
