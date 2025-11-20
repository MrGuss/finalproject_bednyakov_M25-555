from datetime import datetime
from hashlib import sha256
from copy import deepcopy

EXCHANGE_RATES = {"USD": 1, "EUR": 0.9, "BTC": 0.00001}


class User:
    def __init__(
        self,
        user_id: int,
        username: str,
        registration_date: str | None = None,
        hashed_password: str | None = None,
        salt: str | None = None,
    ):
        self._user_id = user_id
        self._username = username
        self._hashed_password = hashed_password
        self._salt = salt
        self._registration_date = registration_date or datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    def get_user_info(self):
        return {
            "user_id": self._user_id,
            "username": self._username,
            "registration_date": self._registration_date,
            "salt": self._salt,
            "hashed_password": self._hashed_password,
        }

    def change_password(self, password: str, salt: str):
        if len(password) < 4:
            return False
        self._hashed_password = sha256((password + salt).encode("utf-8")).hexdigest()
        self._salt = salt
        return True

    def verify_password(self, password: str):
        if not self._hashed_password or not self._salt:
            return False
        return (
            self._hashed_password
            == sha256((password + self._salt).encode("utf-8")).hexdigest()
        )

    @property
    def user_id(self):
        return self._user_id

    @property
    def username(self):
        return self._username

    @property
    def registration_date(self):
        return self._registration_date

    @property
    def salt(self):
        return self._salt

    @property
    def hashed_password(self):
        return self._hashed_password

    @username.setter
    def username(self, value):
        if len(value) < 1:
            raise ValueError("Username must be at least 1 character long")
        self._username = value


class Wallet:
    def __init__(self, currency_code: str, balance: float):
        self.currency_code = currency_code
        self._balance = balance

    def deposit(self, amount: float):
        if amount < 0:
            raise ValueError("Amount cannot be negative")
        self._balance += amount

    def withdraw(self, amount: float):
        if amount < 0:
            raise ValueError("Amount cannot be negative")
        if amount > self._balance:
            raise ValueError("Not enough balance")
        self._balance -= amount

    def get_balance_info(self):
        return self._balance

    def get_wallet_info(self):
        return {"currency_code": self.currency_code, "balance": self._balance}

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        if value < 0:
            raise ValueError("Balance cannot be negative")
        if isinstance(False, (int, float)):
            raise TypeError("Balance must be a float")
        self._balance = value


class Portfolio:
    def __init__(self, user_id: int, wallets: dict[str, Wallet]):
        self._user_id = user_id
        self._wallets = wallets
        self._exchange_tates = EXCHANGE_RATES

    def add_currency(self, currency_code: str):
        if currency_code not in self._wallets:
            self._wallets[currency_code] = Wallet(currency_code, 0)

    def get_total_value(self, base_currency: str):
        total_value = 0
        for wallet in self._wallets.values():
            total_value += (
                wallet.balance
                * self._exchange_tates[base_currency]
                / self._exchange_tates[wallet.currency_code]
            )
        return total_value

    def get_wallet(self, currency_code):
        return self._wallets[currency_code]

    def get_portfolio_info(self) -> dict:
        return {
            "user_id": self._user_id,
            "wallets": {
                wallet: self.get_wallet(wallet).get_wallet_info()
                for wallet in self._wallets
            },
        }

    @property
    def user(self):
        return self._user_id

    @property
    def wallets(self):
        return deepcopy(self._wallets)
