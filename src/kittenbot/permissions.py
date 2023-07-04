from enum import Enum
from typing import List, Callable

from telegram import Update

from .types import TContext

SecurityFunc = Callable[[Update, TContext], "SecurityAction"]


class SecurityAction(Enum):
    DENY = 0
    ALLOW = 1
    UNDEFINED = 3


def whitelist(user_ids: List[int]) -> SecurityFunc:
    def wrapped(update: Update, context: TContext) -> SecurityAction:
        if not update:
            return SecurityAction.UNDEFINED
        if not update.effective_user:
            return SecurityAction.UNDEFINED
        if update.effective_user.id not in user_ids:
            print("permission denied")
            return SecurityAction.DENY
        return SecurityAction.ALLOW
    return wrapped
