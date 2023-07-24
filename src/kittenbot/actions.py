from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

from telegram import Message


class ReplyContent(ABC):
    pass


@dataclass
class RandomResourceReplyContent(ReplyContent):
    category: str


@dataclass
class TextReplyContent(ReplyContent):
    text: str


@dataclass
class DocumentReplyContent(ReplyContent):
    filename: str
    document: bytes


class Action(ABC):
    pass


@dataclass
class Reply(Action):
    reply_to: Message
    content: ReplyContent


@dataclass
class RestrictMember(Action):
    chat_id: int
    user_id: int
    until_date: Optional[datetime]


@dataclass(init=False)
class CompositeAction(Action):
    actions: List[Action]

    def __init__(self, actions: List[Optional[Action]]):
        self.actions = [action for action in actions if action]
