from abc import ABC
from dataclasses import dataclass

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
