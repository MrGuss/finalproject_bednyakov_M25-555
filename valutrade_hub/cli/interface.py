import shlex
from ..core.usecases import register, login, show_portfolio, buy, sell, get_rate


class Arg:
    def __init__(self, arg_name: str, required: bool, value_type: type):
        self.name = arg_name
        self.required = required
        self.value_type = value_type
        self.value = None


class Command:
    def __init__(self, cmd_name: str):
        self.cmd = cmd_name
        self.args = {}

    def add_arg(self, arg_name: str, required: bool, value_type: type):
        if '-' in arg_name:
            arg_name_called = arg_name.replace('-', '')
        else:
            arg_name_called = arg_name

        self.args[arg_name_called] = Arg(arg_name, required, value_type)

    def parse_args(self, cmd: list[str]):

        for arg in self.args:
            arg_object = self.args[arg]
            if arg_object.name in cmd:
                index = cmd.index(arg_object.name)
                try:
                    value = arg_object.value_type(cmd[index + 1])
                except ValueError:
                    raise ValueError(f"Argument {arg} must be of type {arg_object.value_type.__name__}")
                arg_object.value = value
                cmd.pop(index)
                cmd.pop(index)
            else:
                if arg_object.required:
                    raise ValueError(f"Argument {arg} is required for command {self._cmd}")
                else:
                    arg_object.value = None
                    arg_object.parsed = True

        if len(cmd) > 0:
            raise ValueError(f"Unknown arguments {', '.join(cmd)} for command {self._cmd}")

    def __getattr__(self, name):
        try:
            return self.args[name].value
        except KeyError:
            raise AttributeError(name)


class DummyParser:
    def __init__(self):
        self._commands = {}
        self.parsed_command = None

    def add_command(self, cmd_name: str):
        self._commands[cmd_name] = Command(cmd_name)

    def parse(self, cmd: str):
        result = shlex.split(cmd)
        command = result[0]
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
parser.get_rate.add_arg("--from", True, str)
parser.get_rate.add_arg("--to", True, str)


def process_comand(cmd: str):
    parser.parse(cmd)

    try:
        parsed_command = parser.parsed_command
        if parsed_command is not None:
            if parsed_command.cmd == "register":
                register(parsed_command.username, parsed_command.password)
            elif parsed_command.cmd == "login":
                login(parsed_command.username, parsed_command.password)
            elif parsed_command.cmd == "show_portfolio":
                show_portfolio(parsed_command.base)
            elif parsed_command.cmd == "buy":
                buy(parsed_command.currency, parsed_command.amount)
            elif parsed_command.cmd == "sell":
                sell(parsed_command.currency, parsed_command.amount)
            elif parsed_command.cmd == "get_rate":
                get_rate(parsed_command.from_currency, parsed_command.to_currency)
            else:
                print("Unknown command")
        else:
            print("No parsed command found")
    except ValueError as e:
        print("Error:", e)
