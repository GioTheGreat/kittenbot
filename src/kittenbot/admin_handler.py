from typing import Any, Optional

from telegram import Update

from .actions import Action, Reply, TextReplyContent
from .history import History
from .types import HandlerFunc


def get_user_id_handler(hist: History) -> HandlerFunc:
    def _handle(update: Update, context: Any) -> Optional[Action]:
        username = update.message.text.split(" ", maxsplit=1)[1].strip().lstrip("@")
        user_id = hist.get_user_id(username)
        if user_id:
            return Reply(update.message, TextReplyContent(str(user_id)))
        return Reply(update.message, TextReplyContent(f"user id for username {username} not found"))
    return _handle
