import shlex

from ..core.exceptions import ApiRequestError, CurrencyNotFoundError, InsufficientFundsError
from ..core.usecases import buy, get_rate, help_show, login, register, sell, show_portfolio, show_rates, update_rates


class Arg:
    """
    Argument class
    """
    def __init__(self, arg_name: str, required: bool, value_type: type):
        self.name = arg_name
        self.required = required
        self.value_type = value_type
        self.value = None


class Command:
    """
    Command class
    """
    def __init__(self, cmd_name: str):
        self.cmd = cmd_name
        self.args = {}

    def add_arg(self, arg_name: str, required: bool, value_type: type):
        """
        Add argument to command
        :param arg_name: argument name
        :param required: is argument required
        :param value_type: type of argument
        :return: None
        """
        if '-' in arg_name:
            arg_name_called = arg_name.replace('-', '')
        else:
            arg_name_called = arg_name

        self.args[arg_name_called] = Arg(arg_name, required, value_type)

    def parse_args(self, cmd: list[str]):
        """
        Parse arguments from command
        :param cmd: command from user
        :return: None
        """
        for arg in self.args:
            arg_object = self.args[arg]
            if arg_object.name in cmd:
                index = cmd.index(arg_object.name)
                try:
                    value = arg_object.value_type(cmd[index + 1])
                except ValueError:
                    raise ValueError(f"Argument {arg_object.name} must be of type {arg_object.value_type.__name__}")
                except IndexError:
                    raise ValueError(f"Argument for {arg_object.name} cannot be empty")
                arg_object.value = value
                cmd.pop(index)
                cmd.pop(index)
            else:
                if arg_object.required:
                    raise ValueError(f"Argument {arg_object.name} is required for command {self.cmd}")
                else:
                    arg_object.value = None
                    arg_object.parsed = True

        if len(cmd) > 0:
            raise ValueError(f"Unknown arguments {', '.join(cmd)} for command {self.cmd}")

    def __getattr__(self, name):
        try:
            return self.args[name].value
        except KeyError:
            raise AttributeError(name)


class DummyParser:
    """
    Super dummy parser because we are forbidden to use normal one from libraries
    Inspired by argparse
    """
    def __init__(self):
        self._commands = {}
        self.parsed_command = None

    def add_command(self, cmd_name: str):
        """
        Add command to parser
        :param cmd_name: command name
        :return: None
        """
        self._commands[cmd_name] = Command(cmd_name)

    def parse(self, cmd: str):
        """
        Parse command from user
        :param cmd: command from user
        :return: None
        """
        result = shlex.split(cmd)
        command = result[0]
        if command not in self._commands:
            raise ValueError(f"Unknown command {command}")
        if command in self._commands:
            self._commands[command].parse_args(result[1:])
        self.parsed_command = self._commands[command]

    def __getattr__(self, name):
        try:
            return self._commands[name]
        except KeyError:
            raise AttributeError(name)


parser = DummyParser()

parser.add_command("register")
parser.register.add_arg("--username", True, str)
parser.register.add_arg("--password", True, str)

parser.add_command("login")
parser.login.add_arg("--username", True, str)
parser.login.add_arg("--password", True, str)

parser.add_command("show_portfolio")
parser.show_portfolio.add_arg("--base", False, str)

parser.add_command("buy")
parser.buy.add_arg("--currency", True, str)
parser.buy.add_arg("--amount", True, float)

parser.add_command("sell")
parser.sell.add_arg("--currency", True, str)
parser.sell.add_arg("--amount", True, float)

parser.add_command("get_rate")
parser.get_rate.add_arg("--from_cur", True, str)
parser.get_rate.add_arg("--to_cur", True, str)

parser.add_command("update_rates")
parser.update_rates.add_arg("--source", False, str)

parser.add_command("show_rates")
parser.show_rates.add_arg("--currency", False, str)
parser.show_rates.add_arg("--top", False, int)
parser.show_rates.add_arg("--base", False, str)

parser.add_command("help")

parser.add_command("exit")


def process_comand(cmd: str):
    """
    Process command from user
    :param cmd: command from user
    :return: None
    """
    try:
        parser.parse(cmd)
        parsed_command = parser.parsed_command
        if parsed_command is not None:
            if parsed_command.cmd == "register":
                register(username=parsed_command.username, password=parsed_command.password)
            elif parsed_command.cmd == "login":
                login(username=parsed_command.username, password=parsed_command.password)
            elif parsed_command.cmd == "show_portfolio":
                show_portfolio(parsed_command.base)
            elif parsed_command.cmd == "buy":
                buy(currency=parsed_command.currency, amount=parsed_command.amount)
            elif parsed_command.cmd == "sell":
                sell(currency=parsed_command.currency, amount=parsed_command.amount)
            elif parsed_command.cmd == "get_rate":
                get_rate(parsed_command.from_cur, parsed_command.to_cur)
            elif parsed_command.cmd == "exit":
                exit()
            elif parsed_command.cmd == "help":
                help_show()
            elif parsed_command.cmd == "update_rates":
                update_rates(parsed_command.source)
            elif parsed_command.cmd == "show_rates":
                show_rates(parsed_command.currency, parsed_command.top, parsed_command.base)
            else:
                print("Unknown command")
        else:
            print("No parsed command found")
    except ValueError as e:
        print("Error:", e)
    except ApiRequestError as e:
        print("Error:", e)
        print("Try again later")
    except InsufficientFundsError as e:
        print("Error:", e)
    except CurrencyNotFoundError as e:
        print("Error:", e)
        print("Try command 'get-rate' to see all available currencies")
