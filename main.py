import prompt

from valutrade_hub.cli.interface import process_comand


def main():
    while True:
        command = prompt.string("> ")
        process_comand(command)


if __name__ == "__main__":
    main()
