from .utils import get_users, save_users, get_exchange_rates, get_portfolios, exchange, validate, save_portfolios
from random import choice
import string
from .models import User, Portfolio
from ..infra.settings import SettingsLoader
from ..decorators import log_action


session_user_id = None

settings = SettingsLoader("data/config.json")


def register(username: str, password: str) -> None:
    users = get_users()
    for user_id in users:
        if users[user_id].username == username:
            raise ValueError("Username already exists")
    user_id = max(users) + 1
    user = User(user_id, username)
    salt = "".join([choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(10)])
    user.change_password(password, salt)
    users[user_id] = user
    save_users(users)


def login(username: str, password: str) -> None:
    global session_user_id
    if session_user_id:
        raise ValueError("You are already logged in")

    users = get_users()
    for user_id in users:
        if users[user_id].username == username and users[user_id].verify_password(password):
            session_user_id = user_id
            return

    raise ValueError("Invalid username or password")


def show_portfolio(base_currency: str | None = None) -> None:
    if not session_user_id:
        raise ValueError("You are not logged in")

    base_currency = validate(base_currency)

    portfolios = get_portfolios()
    if session_user_id not in portfolios:
        raise ValueError("You have no portfolio")

    portfolio = portfolios[session_user_id]

    for wallet in portfolio.wallets.values():
        print(wallet.balance, wallet.currency_code, "->", exchange(wallet.currency_code, base_currency, wallet.balance), base_currency)


def buy(currency: str, amount: float) -> None:
    if not session_user_id:
        raise ValueError("You are not logged in")

    currency = validate(currency)
    if amount < 0:
        raise ValueError("Amount cannot be negative")

    portfolios = get_portfolios()
    if session_user_id not in portfolios:
        portfolio = Portfolio(session_user_id, {})
        portfolios[session_user_id] = portfolio
    else:
        portfolio = portfolios[session_user_id]

    if currency not in portfolio.wallets:
        portfolio.add_currency(currency)

    before_amount = portfolio.get_wallet(currency).balance
    portfolio.get_wallet(currency).deposit(amount)
    print(f"Покупка выполнена: {amount} {currency} по курсу {get_exchange_rates()['currencies'][currency]} USD/{currency}")
    print("Изменения в портфеле:")
    print(f"- {currency}: было {before_amount} → стало {portfolio.get_wallet(currency).balance}")

    save_portfolios(portfolios)


def sell(currency: str, amount: float) -> None:
    if not session_user_id:
        raise ValueError("You are not logged in")

    currency = validate(currency)
    if amount < 0:
        raise ValueError("Amount cannot be negative")

    portfolios = get_portfolios()
    if session_user_id not in portfolios:
        portfolio = Portfolio(session_user_id, {})
        portfolios[session_user_id] = portfolio
    else:
        portfolio = portfolios[session_user_id]

    if currency not in portfolio.wallets:
        raise ValueError("You have no such currency in your portfolio")

    before_amount = portfolio.get_wallet(currency).balance
    portfolio.get_wallet(currency).withdraw(amount)

    print(f"Продажа выполнена: {amount} {currency} по курсу {get_exchange_rates()['currencies'][currency]} USD/{currency}")
    print("Изменения в портфеле:")
    print(f"- {currency}: было {before_amount} → стало {portfolio.get_wallet(currency).balance}")

    save_portfolios(portfolios)


def get_rate(from_currency: str, to_currency: str) -> None:

    from_currency = validate(from_currency)
    to_currency = validate(to_currency)

    exchange_rates = get_exchange_rates()

    print(f"Курс {from_currency}→{to_currency}: {exchange_rates['currencies'][from_currency]/exchange_rates['currencies'][to_currency]}"
          f" ({exchange_rates['updated']})")
    print(f"Обратный курс {to_currency}→{from_currency}: {exchange_rates['currencies'][to_currency]/exchange_rates['currencies'][from_currency]}")


def help_show() -> None:
    print("Available commands:")
    print("register --username <username> --password <password>")
    print("login --username <username> --password <password>")
    print("show_portfolio --base <currency>")
    print("buy --currency <currency> --amount <amount>")
    print("sell --currency <currency> --amount <amount>")
    print("get_rate --from_cur <currency> --to_cur <currency>")
    print("exit")
    print("help")
