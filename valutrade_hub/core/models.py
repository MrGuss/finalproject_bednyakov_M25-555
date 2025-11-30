from copy import deepcopy
from datetime import datetime
from hashlib import sha256
from typing import Optional

from .exceptions import InsufficientFundsError


class User:
    """
    User class
    :param user_id: user id
    :param username: username
    :param registration_date: registration date
    :param hashed_password: hashed password
    :param salt: salt
    """
    def __init__(
        self,
        user_id: int,
        username: str,
        registration_date: Optional[str] = None,
        hashed_password: Optional[str] = None,
        salt: Optional[str] = None,
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
        """
        Change password safely
        :param password: password
        :param salt: salt
        :return: True if password is changed, False otherwise
        """
        if len(password) <= 4:
            return False
        self._hashed_password = sha256((password + salt).encode("utf-8")).hexdigest()
        self._salt = salt
        return True

    def verify_password(self, password: str):
        """
        Verify password
        :param password: password
        :return: True if password is correct, False otherwise
        """
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
    """
    Wallet class
    :param currency_code: currency code
    :param balance: balance
    """
    def __init__(self, currency_code: str, balance: float):
        self.currency_code = currency_code
        self._balance = balance

    def deposit(self, amount: float):
        """
        Deposit amount to wallet
        :param amount: amount of currency
        :return: None
        """
        if amount < 0:
            raise ValueError("Amount cannot be negative")
        self._balance += amount

    def withdraw(self, amount: float):
        """
        Withdraw amount from wallet
        :param amount: amount of currency
        :return: None
        """
        if amount < 0:
            raise ValueError("Amount cannot be negative")
        if amount > self._balance:
            raise InsufficientFundsError(
                available_funds=self._balance, required_funds=amount, code=self.currency_code)
        self._balance -= amount

    def get_balance_info(self):
        return self._balance

    def get_wallet_info(self):
        """
        Get wallet info
        :return: wallet info
        """
        return {"currency_code": self.currency_code, "balance": self._balance}

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        """
        Set balance
        :param value: balance
        :return: None
        """
        if value < 0:
            raise ValueError("Balance cannot be negative")
        if isinstance(False, (int, float)):
            raise TypeError("Balance must be a float")
        self._balance = value


class Portfolio:
    """
    Portfolio class
    :param user_id: user id
    :param wallets: wallets
    """
    def __init__(self, user_id: int, wallets: dict[str, Wallet]):
        self._user_id = user_id
        self._wallets = wallets

    def add_currency(self, currency_code: str):
        """
        Add currency to portfolio
        :param currency_code: currency code
        :return: None
        """
        if currency_code not in self._wallets:
            self._wallets[currency_code] = Wallet(currency_code, 0)

    def get_total_value(self, base_currency: str, exchange_rates: dict):
        """
        Get total value of portfolio
        :param base_currency: base currency
        :param exchange_rates: exchange rates
        :return: total value
        """
        total_value = 0
        for wallet in self._wallets.values():
            total_value += (
                wallet.balance
                * exchange_rates[base_currency]
                / exchange_rates[wallet.currency_code]
            )
        return total_value

    def get_wallet(self, currency_code):
        """
        Get wallet
        :param currency_code: currency code
        :return: wallet
        """
        return self._wallets[currency_code]

    def get_portfolio_info(self) -> dict:
        """
        Get portfolio info
        :return: portfolio info
        """
        return {
            "user_id": self._user_id,
            "wallets": {
                wallet: self.get_wallet(wallet).get_wallet_info()
                for wallet in self._wallets
            },
        }

    @property
    def user(self) -> int:
        return self._user_id

    @property
    def wallets(self) -> dict[str, Wallet]:
        return deepcopy(self._wallets)
