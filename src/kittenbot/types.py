from typing import TypeVar, Callable, Optional

from telegram import Update

from .actions import Action

TContext = TypeVar("TContext")
HandlerFunc = Callable[[Update, TContext], Optional[Action]]
