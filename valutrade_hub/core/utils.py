import json
from .models import User, Portfolio, Wallet
from .exceptions import ApiRequestError, CurrencyNotFoundError
from ..infra.settings import SettingsLoader

settings = SettingsLoader("data/config.json")


def get_users():
    with open(f"{settings.data_path}/users.json", "r") as f:
        users_json = json.load(f)
    users = {}
    for user in users_json:
        users[user["user_id"]] = User(**user)

    return users


def save_users(users):
    with open(f"{settings.data_path}/users.json", "w") as f:
        json.dump([user.get_user_info() for user in users.values()], f, indent=2)


def get_portfolios():
    with open(f"{settings.data_path}/portfolios.json", "r") as f:
        portfolios_json = json.load(f)
    portfolios = {}
    for portfolio in portfolios_json:
        wallets = {}
        for wallet in portfolio["wallets"]:
            wallets[wallet] = Wallet(wallet, portfolio["wallets"][wallet]["balance"])
        portfolios[portfolio["user_id"]] = Portfolio(portfolio["user_id"], wallets)

    return portfolios


def save_portfolios(portfolios: dict[int, Portfolio]):
    with open(f"{settings.data_path}/portfolios.json", "w") as f:
        json.dump([portfolio.get_portfolio_info() for portfolio in portfolios.values()], f, indent=2)


def get_exchange_rates():
    try:
        with open(f"{settings.data_path}/rates.json", "r") as f:
            exchange_rates = json.load(f)
        return exchange_rates
    except FileNotFoundError:
        raise ApiRequestError("Exchange rates not found")


def exchange(from_currency: str, to_currency: str, amount: float):
    exchange_rates = get_exchange_rates()
    return amount*exchange_rates["currencies"][from_currency]/exchange_rates["currencies"][to_currency]


def validate(currency: str | None) -> str:
    if currency is None:
        return settings.default_base_currency
    if currency.upper() not in get_exchange_rates()["currencies"]:
        raise CurrencyNotFoundError(currency.upper())

    return currency.upper()
