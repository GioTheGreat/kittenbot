from typing import Awaitable, Any

from telegram.ext import BaseUpdateProcessor

from .history import History


class StoringUpdateProcessorWrapper(BaseUpdateProcessor):
    def __init__(self, history: History):
        super().__init__(1)
        self.history = history

    async def do_process_update(self, update: object, coroutine: "Awaitable[Any]") -> None:
        try:
            if update.message:
                self.history.store(update.message)
        finally:
            await coroutine

    async def initialize(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass
