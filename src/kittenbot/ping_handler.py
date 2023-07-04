from typing import Any, Optional

from telegram import Update

from .actions import Action, Reply, TextReplyContent


def ping(update: Update, context: Any) -> Optional[Action]:
    print("received ping command")
    return Reply(update.message, TextReplyContent("pong"))
