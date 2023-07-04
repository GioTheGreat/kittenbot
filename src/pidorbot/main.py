from pymorphy3.analyzer import MorphAnalyzer
from telegram.ext import ApplicationBuilder, MessageHandler, filters

from .config import PidorConfig
from .handler import PidorHandler
from .random_generator import BinaryRandomGenerator


def main():
    config = PidorConfig()
    if config.token is None:
        print("Token is not set, exit")
        exit(1)
    app = ApplicationBuilder().token(config.token).build()
    handler = PidorHandler(
        BinaryRandomGenerator(config.probability),
        MorphAnalyzer())
    app.add_handler(MessageHandler(filters.ALL, handler.handle))
    print("Pidorbot is listening")
    app.run_polling()
