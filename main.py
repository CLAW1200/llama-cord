from argparse import ArgumentParser
from dotenv import load_dotenv
import logging
from core import Bot

if __name__ == "__main__":
    parser = ArgumentParser(prog="Bot")
    parser.add_argument(
        "-d",
        "--debug",
        dest="cogs",
        action="extend",
        nargs="*",
        help="run in debug mode",
    )
    parser.add_argument(
        "-s",
        "--sync",
        action="store_true",
        help="synchronize commands",
    )
    parser.add_argument(
        "-t",
        "--test",
        action="store_true",
        help="use test token",
    )
    args = parser.parse_args()
    debug = args.cogs is not None

    load_dotenv(".env")

    logger = logging.getLogger("discord")
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    handler = logging.FileHandler(
        filename="discord.log", encoding="utf-8", mode="w"
    )
    handler.formatter = logging.Formatter(
        "[%(asctime)s %(levelname)s] %(name)s: %(message)s",
        "%d/%m/%y %H:%M:%S",
    )
    logger.addHandler(handler)
    
    bot = Bot()
    bot.run(debug=debug, cogs=args.cogs, sync=args.sync, test=args.test)
