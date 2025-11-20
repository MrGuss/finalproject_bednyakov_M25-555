from valutrade_hub.cli.interface import process_comand
import prompt


def run():
    while True:
        command = prompt.string("> ")
        process_comand(command)


if __name__ == "__main__":
    run()
