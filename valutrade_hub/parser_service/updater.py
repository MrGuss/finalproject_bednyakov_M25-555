from .config import ParserConfig
from .api_clients import CoinGeckoClient, ExchangeratesApiClient
from .storage import save_rates
from datetime import datetime
from time import time
from ..core.exceptions import ApiRequestError
config = ParserConfig()


class RatesUpdater:
    def __init__(self):
        self.coingecko_client = CoinGeckoClient()
        self.exchangerates_client = ExchangeratesApiClient(config.exchangerates_api_key)

    def run_update(self, source: str | None = None):
        before = time()
        errors = []
        if source == "coin_gecko" or source is None:
            print("[INFO] Fetching rates from CoinGecko...")
            try:
                rates_cg = self.coingecko_client.fetch_rates()
                print("[INFO] Rates fetched from CoinGecko")
            except ApiRequestError as e:
                errors.append(e)
                rates_cg = {}
                print("[ERROR] Failed to fetch from CoinGecko: Network error")

            for rate in rates_cg:
                rates_cg[rate] = {
                    "rate": rates_cg[rate],
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "source": "coin_gecko",
                }
        else:
            rates_cg = {}

        if source == "exchange_rates" or source is None:
            print("[INFO] Fetching rates from ExchangeratesAPI...")
            try:
                rates_ex = self.exchangerates_client.fetch_rates()
                print("[INFO] Rates fetched from ExchangeratesAPI")
            except ApiRequestError as e:
                errors.append(e)
                rates_ex = {}
                print("[ERROR] Failed to fetch from ExchangeratesAPI: Network error")

            for rate in rates_ex:
                rates_ex[rate] = {
                    "rate": rates_ex[rate],
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "source": "exchange_rates",
                }
        else:
            rates_ex = {}
        now = time()

        rates = {**rates_cg, **rates_ex}
        print(f"[INFO] Writing {len(rates)} rates to data/rates.json...")
        save_rates(rates, now - before)
        for error in errors:
            raise error
