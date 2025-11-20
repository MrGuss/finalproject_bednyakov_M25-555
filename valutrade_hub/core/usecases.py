from .utils import get_users, save_users, get_exchange_rates, get_portfolios, exchange
from random import choice
import string
from .models import User

session_user_id = None


def register(username: str, password: str) -> None:
    """
    1.    Проверить уникальность username в users.json.
    2.    Сгенерировать user_id (например, автоинкремент).
    3.    Захешировать пароль (делайте односторонний псевдо-хеш (например, hashlib.sha256(password + salt)), соль храните рядом.).
    4.    Сохранить пользователя в users.json.
    5.    Создать пустой портфель (portfolios.json: user_id + пустой словарь кошельков).
    6.    Вернуть сообщение об успехе.
    """
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


def login(username: str, password: str):
    global session_user_id
    if session_user_id:
        raise ValueError("You are already logged in")

    users = get_users()
    for user_id in users:
        if users[user_id].username == username and users[user_id].verify_password(password):
            session_user_id = user_id
            return

    raise ValueError("Invalid username or password")


def show_portfolio(base_currency: str | None = None):
    if not base_currency:
        base_currency = "USD"
    """
    1.    Убедиться, что пользователь залогинен.
    2.    Загрузить портфель пользователя.
    3.    Если кошельков нет — сообщить об этом.
    4.    Для каждого кошелька:
        *    показать currency_code, баланс;
        *    посчитать стоимость в base по текущим курсам;
    5.    Показать сумму по всем кошелькам в base.
    """
    if not session_user_id:
        raise ValueError("You are not logged in")

    portfolios = get_portfolios()
    if session_user_id not in portfolios:
        raise ValueError("You have no portfolio")

    portfolio = portfolios[session_user_id]

    for wallet in portfolio.wallets.values():
        print(wallet.balance, wallet.currency_code, "->", exchange(wallet.currency_code, base_currency, wallet.balance), base_currency)


def buy(currency: str, amount: float) -> bool:
    pass


def sell(currency: str, amount: float) -> bool:
    pass


def get_rate(from_currency: str, to_currency: str) -> float:
    pass
