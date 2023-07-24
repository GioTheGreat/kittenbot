from typing import Coroutine, Any, Callable, Optional

from telegram import Update

from .interpreter import Interpreter
from .permissions import SecurityFunc, SecurityAction
from .types import HandlerFunc, TContext


PipelineFunc = Callable[[Update, TContext], Coroutine[Any, Any, None]]


def pipeline(
        security: SecurityFunc,
        handler: HandlerFunc,
        interpreter: Interpreter
) -> PipelineFunc:
    async def wrapped(update: Update, context: TContext) -> None:
        if security(update, context) == SecurityAction.DENY:
            return
        if not (action := handler(update, context)):
            return
        await interpreter.run_action(action)
    return wrapped
