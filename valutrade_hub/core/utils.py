import json

from ..infra.settings import SettingsLoader
from .models import Portfolio, User, Wallet

settings = SettingsLoader("data/config.json")


def get_users():
    """
    Get users from local data storage
    :return: dict of users
    """
    try:
        with open(f"{settings.data_path}/users.json", "r") as f:
            users_json = json.load(f)
    except FileNotFoundError:
        return []
    except json.decoder.JSONDecodeError:
        return []

    with open(f"{settings.data_path}/users.json", "r") as f:
        users_json = json.load(f)
    users = {}
    for user in users_json:
        users[user["user_id"]] = User(**user)

    return users


def save_users(users):
    """
    Save users to local data storage
    :param users: dict of users
    :return: None
    """
    with open(f"{settings.data_path}/users.json", "w") as f:
        json.dump([user.get_user_info() for user in users.values()], f, indent=2)


def get_portfolios():
    """
    Get portfolios from local data storage
    :return: dict of portfolios
    """
    try:
        with open(f"{settings.data_path}/portfolios.json", "r") as f:
            portfolios_json = json.load(f)
    except FileNotFoundError:
        return {}
    except json.decoder.JSONDecodeError:
        return {}

    portfolios = {}
    for portfolio in portfolios_json:
        wallets = {}
        for wallet in portfolio["wallets"]:
            wallets[wallet] = Wallet(wallet, portfolio["wallets"][wallet]["balance"])
        portfolios[portfolio["user_id"]] = Portfolio(portfolio["user_id"], wallets)

    return portfolios


def save_portfolios(portfolios: dict[int, Portfolio]):
    """
    Save portfolios to local data storage
    :param portfolios: dict of portfolios
    :return: None
    """
    with open(f"{settings.data_path}/portfolios.json", "w") as f:
        json.dump([portfolio.get_portfolio_info() for portfolio in portfolios.values()], f, indent=2)
