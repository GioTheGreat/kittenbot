from typing import Any, Optional

from loguru import logger
from telegram import Update

from .actions import Action, Reply, TextReplyContent


def ping(update: Update, context: Any) -> Optional[Action]:
    logger.info("received ping command")
    return Reply(update.message, TextReplyContent("pong"))
