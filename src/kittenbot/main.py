import os

from pymorphy3.analyzer import MorphAnalyzer
from sqlalchemy import create_engine
from telegram.ext import ApplicationBuilder, filters, CommandHandler, MessageHandler

from .admin_handler import get_user_id_handler
from .config import BotConfig
from .pipelines import pipeline
from .message_handler import KittenMessageHandler
from .history import History
from .interpreter import Interpreter
from .language_processing import Nlp
from .permissions import allow_all, whitelist
from .ping_handler import ping
from .random_generator import RandomGenerator
from .resources import ProdResources
from .update_processor import StoringUpdateProcessorWrapper


def main():
    config = BotConfig()
    if config.token is None:
        print("Token is not set, exit")
        exit(1)

    try:
        os.remove("bot.sqlite")
    except Exception:
        pass
    engine = create_engine("sqlite:///bot.sqlite")
    hist = History(engine)
    rand_gen = RandomGenerator()
    resources = ProdResources(rand_gen, "resources")
    self_user_id = int(config.token.split(":")[0])
    message_handler = KittenMessageHandler(
        rand_gen,
        resources,
        Nlp(MorphAnalyzer()),
        self_user_id,
        config.probability,
        config.agree_probability,
        config.test_group_ids,
        config.bot_names,
        config.noun_template,
    )

    app = (ApplicationBuilder()
           .concurrent_updates(StoringUpdateProcessorWrapper(hist))
           .token(config.token)
           .build())

    interpreter = Interpreter(app.bot)
    security = whitelist(config.admin_user_ids)
    app.add_handlers([
        CommandHandler("ping", pipeline(allow_all, ping, interpreter)),
        CommandHandler("get_user_id", pipeline(security, get_user_id_handler(hist), interpreter)),
        MessageHandler(~filters.COMMAND, pipeline(allow_all, message_handler.handle, interpreter)),
    ])
    print("Bot is listening")
    app.run_polling()
