import datetime
import string
from random import choice

from valutrade_hub.core.exceptions import InsufficientFundsError

from ..decorators import log_action
from ..infra.settings import SettingsLoader
from ..parser_service.updater import RatesUpdater
from .currencies import exchange, get_cur_rate, get_currency, get_exchange_rates
from .models import Portfolio, User
from .utils import (
    get_portfolios,
    get_users,
    save_portfolios,
    save_users,
)

session_user_id = None

settings = SettingsLoader("data/config.json")


@log_action
def register(username: str, password: str) -> None:
    """
    Register new user
    :param username: username
    :param password: password
    :return: None
    """
    users = get_users()
    for user_id in users:
        if users[user_id].username == username:
            raise ValueError("Username already exists")
    user_id = max(users) + 1
    user = User(user_id, username)
    portfolios = get_portfolios()
    portfolio = Portfolio(user_id, {})
    portfolio.add_currency(settings.default_base_currency)
    portfolio.get_wallet(settings.default_base_currency).deposit(1000)
    portfolios[user_id] = portfolio
    save_portfolios(portfolios)
    salt = "".join(
        [
            choice(string.ascii_letters + string.digits + string.punctuation)
            for _ in range(10)
        ]
    )
    if not user.change_password(password, salt):
        raise ValueError("Password should be longer then 4 characters")

    users[user_id] = user
    save_users(users)


@log_action
def login(username: str, password: str) -> None:
    """
    Login user
    :param username: username
    :param password: password
    :return: None
    """
    global session_user_id
    if session_user_id:
        raise ValueError("You are already logged in")

    users = get_users()
    for user_id in users:
        if users[user_id].username == username and users[user_id].verify_password(
            password
        ):
            session_user_id = user_id
            return

    raise ValueError("Invalid username or password")


def show_portfolio(base_currency: str | None = None) -> None:
    """
    Show portfolio of current user
    :param base_currency: base currency
    :return: None
    """
    if not session_user_id:
        raise ValueError("You are not logged in")

    base_currency_object = get_currency(base_currency)

    portfolios = get_portfolios()
    if session_user_id not in portfolios:
        raise ValueError("You have no portfolio")

    portfolio = portfolios[session_user_id]

    for wallet in portfolio.wallets.values():
        print(
            wallet.balance,
            wallet.currency_code,
            "->",
            exchange(wallet.currency_code, base_currency_object.name, wallet.balance),
            base_currency_object.code,
        )


@log_action
def buy(currency: str, amount: float) -> None:
    """
    Buy currency for current user
    :param currency: currency code
    :param amount: amount of currency
    :return: None
    """
    if not session_user_id:
        raise ValueError("You are not logged in")

    currency_object = get_currency(currency)

    if currency_object.code == settings.default_base_currency:
        raise ValueError("You cannot buy the base currency")

    if amount <= 0:
        raise ValueError("Amount cannot be negative")

    portfolios = get_portfolios()
    if session_user_id not in portfolios:
        portfolio = Portfolio(session_user_id, {})
        portfolios[session_user_id] = portfolio
    else:
        portfolio = portfolios[session_user_id]

    if currency_object.code not in portfolio.wallets:
        portfolio.add_currency(currency_object.code)

    before_amount = portfolio.get_wallet(currency_object.code).balance
    portfolio.get_wallet(settings.default_base_currency).withdraw(
        exchange(currency_object.code, settings.default_base_currency, amount)
    )
    portfolio.get_wallet(currency_object.code).deposit(amount)
    print(
        f"Покупка выполнена: {amount} {currency_object.code} по курсу "
        f"{get_cur_rate(currency_object.code)['rate']} USD/{currency_object.code}"
    )
    print("Изменения в портфеле:")
    print(
        f"- {currency_object.code}: было {before_amount} → стало {portfolio.get_wallet(currency_object.code).balance}"
    )

    save_portfolios(portfolios)


@log_action
def sell(currency: str, amount: float) -> None:
    """
    Sell currency for current user
    :param currency: currency code
    :param amount: amount of currency
    :return: None
    """
    if not session_user_id:
        raise ValueError("You are not logged in")

    currency_object = get_currency(currency)

    if currency_object.code == settings.default_base_currency:
        raise ValueError("You cannot sell the base currency")

    if amount < 0:
        raise ValueError("Amount cannot be negative")

    portfolios = get_portfolios()
    if session_user_id not in portfolios:
        portfolio = Portfolio(session_user_id, {})
        portfolios[session_user_id] = portfolio
    else:
        portfolio = portfolios[session_user_id]

    if currency_object.code not in portfolio.wallets:
        raise InsufficientFundsError(
            available_funds=0,
            required_funds=amount,
            code=currency_object.code,
        )

    before_amount = portfolio.get_wallet(currency_object.code).balance
    portfolio.get_wallet(currency_object.code).withdraw(amount)
    portfolio.get_wallet(settings.default_base_currency).deposit(
        exchange(currency_object.code, settings.default_base_currency, amount)
    )
    print(
        f"Продажа выполнена: {amount} {currency_object.code} по курсу "
        f"{get_cur_rate(currency_object.code)['rate']} USD/{currency_object.code}"
    )
    print("Изменения в портфеле:")
    print(
        f"- {currency_object.code}: было {before_amount} → стало {portfolio.get_wallet(currency_object.code).balance}"
    )

    save_portfolios(portfolios)


def get_rate(from_currency: str, to_currency: str) -> None:
    """
    Get currency rate
    :param from_currency: from currency code
    :param to_currency: to currency code
    :return: None
    """
    from_currency_object = get_currency(from_currency)
    to_currency_object = get_currency(to_currency)

    print(
        f"Курс {from_currency_object.code}→{to_currency_object.code}: "
        f"{get_cur_rate(from_currency_object.code)['rate']/get_cur_rate(to_currency_object.code)['rate']}"
        f" ({get_cur_rate(from_currency_object.code)['rate']})"
    )
    print(
        f"Обратный курс {to_currency_object.code}→{from_currency_object.code}: "
        f"{get_cur_rate(to_currency_object.code)['rate']/get_cur_rate(from_currency_object.code)['rate']}"
    )


def help_show() -> None:
    """
    Show help
    :return: None
    """
    print("Available commands:")
    print("register --username <username> --password <password>")
    print("login --username <username> --password <password>")
    print("show_portfolio --base <currency>")
    print("buy --currency <currency> --amount <amount>")
    print("sell --currency <currency> --amount <amount>")
    print("get_rate --from_cur <currency> --to_cur <currency>")
    print("update_rates --source <source>")
    print("show_rates --currency <currency> --top <number> --base <currency>")
    print("exit")
    print("help")


def update_rates(source: str | None = None) -> None:
    """
    Update rates in cache
    :param source: source of rates
    :return: None
    """
    rates_updater = RatesUpdater()
    print("Updating rates...")
    rates_updater.run_update(source)
    print("Rates updated")


def show_rates(currency: str | None, top: int | None, base: str | None) -> None:
    """
    Show rates from last update of cache
    :param currency: currency code
    :param top: number of top rates
    :param base: base currency code
    :return: None
    """
    rates = get_exchange_rates()
    currency = currency.upper() if currency else None
    base = base.upper() if base else None

    if currency and top:
        raise ValueError("You can't use --currency and --top together")

    if currency:
        rate = get_cur_rate(currency, base)
        print(
            f"Курс {currency}→{base or settings.default_base_currency}: {rate['rate']} ({rate['updated_at']})"
        )
        if datetime.datetime.now() - datetime.datetime.strptime(
            rate["updated_at"], "%Y-%m-%d %H:%M:%S"
        ) > datetime.timedelta(seconds=settings.rates_ttl_seconds):
            print("Курс устарел, обновите курсы с помощью команды update_rates")
        return

    if top:
        rates = sorted(rates["pairs"].items(), key=lambda x: x[1]["rate"], reverse=True)
        rates = rates[:top]
        print(f"Топ-{top} курсов по курсу {base or settings.default_base_currency}:")
        print(
            "\n".join(
                [
                    f"{pair.split('_')[0]}→{base or settings.default_base_currency}:"
                    f" {get_cur_rate(pair.split('_')[0], base)['rate']} ({rate['updated_at']})"
                    for pair, rate in rates
                ]
            )
        )
        for pair, rate in rates:
            if datetime.datetime.now() - datetime.datetime.strptime(
                rate["updated_at"], "%Y-%m-%d %H:%M:%S"
            ) > datetime.timedelta(seconds=settings.rates_ttl_seconds):
                print(
                    "Один или больше курсов устарели, обновите курсы с помощью команды update_rates"
                )
                return
        return

    if not currency and not top:
        print(
            "\n".join(
                [
                    f"{pair.split('_')[0]}→{base or settings.default_base_currency}:"
                    f" {get_cur_rate(pair.split('_')[0], base)['rate']} ({rate['updated_at']})"
                    for pair, rate in rates["pairs"].items()
                ]
            )
        )
        for pair, rate in rates["pairs"].items():
            if datetime.datetime.now() - datetime.datetime.strptime(
                rate["updated_at"], "%Y-%m-%d %H:%M:%S"
            ) > datetime.timedelta(seconds=settings.rates_ttl_seconds):
                print(
                    "Один или больше курсов устарели, обновите курсы с помощью команды update_rates"
                )
                return
        return
