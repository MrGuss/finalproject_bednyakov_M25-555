from valutrade_hub.core.exceptions import InsufficientFundsError
from .utils import (
    get_users,
    save_users,
    get_portfolios,
    save_portfolios,
)
from random import choice
import string
from .models import User, Portfolio
from ..infra.settings import SettingsLoader
from .currencies import get_currency, get_cur_rate, exchange, get_exchange_rates
from ..decorators import log_action
from ..parser_service.updater import RatesUpdater

session_user_id = None

settings = SettingsLoader("data/config.json")


@log_action
def register(username: str, password: str) -> None:
    users = get_users()
    for user_id in users:
        if users[user_id].username == username:
            raise ValueError("Username already exists")
    user_id = max(users) + 1
    user = User(user_id, username)
    salt = "".join(
        [
            choice(string.ascii_letters + string.digits + string.punctuation)
            for _ in range(10)
        ]
    )
    user.change_password(password, salt)
    users[user_id] = user
    save_users(users)


@log_action
def login(username: str, password: str) -> None:
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
            base_currency,
        )


@log_action
def buy(currency: str, amount: float) -> None:
    if not session_user_id:
        raise ValueError("You are not logged in")

    currency_object = get_currency(currency)
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
    if not session_user_id:
        raise ValueError("You are not logged in")

    currency_object = get_currency(currency)

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
    print("Available commands:")
    print("register --username <username> --password <password>")
    print("login --username <username> --password <password>")
    print("show_portfolio --base <currency>")
    print("buy --currency <currency> --amount <amount>")
    print("sell --currency <currency> --amount <amount>")
    print("get_rate --from_cur <currency> --to_cur <currency>")
    print("exit")
    print("help")


def update_rates(source: str | None = None) -> None:
    rates_updater = RatesUpdater()
    print("Updating rates...")
    rates_updater.run_update(source)
    print("Rates updated")


def show_rates(currency: str | None, top: int | None, base: str | None) -> None:
    rates = get_exchange_rates()

    if currency and top:
        raise ValueError("You can't use --currency and --top together")

    if currency:
        rate = get_cur_rate(currency.upper(), base.upper())
        print(
            f"Курс {currency}→{base or settings.default_base_currency}: {rate['rate']} ({rate['updated_at']})"
        )

    if top:
        # TODO: FIX THIS PIECE OF CRAP
        rates = sorted(rates.items(), key=lambda x: x[1]["rate"], reverse=True)
        rates = rates[:top]
        print(
            f"Топ-{top} курсов по курсу {base or settings.default_base_currency}:"
            "\n".join(
                [
                    f"{pair.split('_')[0]}→{base or settings.default_base_currency}:"
                    f" {get_cur_rate(pair.split('_')[0], base)['rate']} ({rate['updated_at']})"
                    for pair, rate in rates
                ]
            )
        )

    if not currency and not top:
        # TODO: FIX THIS PIECE OF CRAP
        print(
            "\n".join(
                [
                    f"{pair.split('_')[0]}→{base or settings.default_base_currency}:"
                    f" {get_cur_rate(pair.split('_')[0], base)['rate']} ({rate['updated_at']})"
                    for pair, rate in rates.items()
                ]
            )
        )#