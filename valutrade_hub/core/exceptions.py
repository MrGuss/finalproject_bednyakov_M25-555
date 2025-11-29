class InsufficientFundsError(Exception):
    """
    Exception for insufficient funds of user wallet
    """
    def __init__(
        self,
        available_funds: float,
        required_funds: float,
        code: str,
        msg="Недостаточно средств: доступно {available} {code}, требуется {required} {code}",
    ):
        self.msg = msg.format(
            available=available_funds, required=required_funds, code=code
        )
        super().__init__(self.msg)

    def __str__(self):
        return f"{self.msg}"


class CurrencyNotFoundError(Exception):
    """
    Exception for currency not found in cache
    """
    def __init__(self, code: str, msg="Неизвестная валюта '{code}'"):
        self.msg = msg.format(code=code)
        super().__init__(self.msg)

    def __str__(self):
        return self.msg


class ApiRequestError(Exception):
    """
    Exception for api request error
    """
    def __init__(self, reason: str, msg="API: {reason}"):
        self.msg = msg.format(reason=reason)
        super().__init__(self.msg)

    def __str__(self):
        return self.msg
