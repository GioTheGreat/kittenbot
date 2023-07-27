from typing import Coroutine, Any, Callable, Optional

from loguru import logger
from telegram import Update

from .actions import Action, RestrictMember, CompositeAction
from .clock import Clock
from .interpreter import Interpreter
from .permissions import SecurityFunc, SecurityAction
from .slowmode_user_repository import SlowmodeUserRepository
from .types import HandlerFunc, TContext

PipelineFunc = Callable[[Update, TContext], Coroutine[Any, Any, None]]


def pipeline(
        security: SecurityFunc,
        handler: HandlerFunc,
        interpreter: Interpreter
) -> PipelineFunc:
    async def wrapped(update: Update, context: TContext) -> None:
        with logger.catch():
            if security(update, context) == SecurityAction.DENY:
                return
            action = handler(update, context)
            if not action:
                return
            await interpreter.run_action(action)
    return wrapped


def slowmode_support(repository: SlowmodeUserRepository, clock: Clock):
    def wrapper(handler: HandlerFunc) -> HandlerFunc:
        def wrapped(update: Update, context: TContext) -> Optional[Action]:
            result = handler(update, context)
            if not update.effective_chat or not update.effective_user:
                return result
            if restriction := repository.get_active_restriction(update.effective_chat.id, update.effective_user.id):
                return CompositeAction([
                    result,
                    RestrictMember(
                        update.effective_chat.id,
                        update.effective_user.id,
                        clock.now() + restriction.interval)
                ])
            else:
                return result
        return wrapped
    return wrapper
