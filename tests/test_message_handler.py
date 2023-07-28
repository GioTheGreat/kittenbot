import datetime
from string import Template
from typing import Optional

import pytest
from attr import define, field
from pymorphy3 import MorphAnalyzer
from telegram import Update, Message, Chat, User

from kittenbot.actions import Reply, DocumentReplyContent, TextReplyContent
from kittenbot.message_handler import KittenMessageHandler
from kittenbot.language_processing import Nlp
from kittenbot.random_generator import RandomGenerator
from kittenbot.resources import Resource, Resources


@define
class TestResource(Resource):
    name: str
    content: bytes

    def get_bytes(self) -> bytes:
        return self.content


class TestResources(Resources[TestResource]):
    def get_random_resource(self, directory: str) -> TestResource:
        return TestResource(directory, b"test")


@pytest.fixture(scope="session")
def morph_analyzer():
    return MorphAnalyzer()


@pytest.fixture(scope="function")
def handler(morph_analyzer):
    return KittenMessageHandler(
        RandomGenerator(),
        TestResources(),
        Nlp(morph_analyzer),
        1,
        1.0,
        1.0,
        [],
        ["котобот"],
        Template("$subj для котиков"),
        noun_weight=1.0,
        verb_template=Template("$verb себе котика"),
        verb_weight=1.0,
    )


@pytest.mark.parametrize("message_text", ["котобот для котиков", "котоботы для котиков"])
def test_izvinis_by_name(handler, message_text):
    message = make_message(message_text)
    actual = handler.handle(Update(0, message), None)
    expected = Reply(message, DocumentReplyContent("izvinis", b"test"))
    assert actual == expected


def test_izvinis_you(handler):
    bot_message = MessageBuilder("тест").from_user(User(handler.self_user_id, "котобот", True)).build()
    user_message = MessageBuilder("ты для котиков").reply_to_message(bot_message).build()
    actual = handler.handle(Update(0, user_message), None)
    expected = Reply(user_message, DocumentReplyContent("izvinis", b"test"))
    assert actual == expected


def test_verb(handler):
    handler.verb_weight = 1.0
    handler.noun_weight = 0.0
    handler.action_probability = 1.0
    user_message = make_message("купят")
    actual = handler.handle(Update(0, user_message), None)
    expected = Reply(user_message, TextReplyContent("купи себе котика"))
    assert actual == expected


def test_hello(handler):
    user_message = make_message("привет")
    actual = handler.handle(Update(0, user_message), None)
    expected = Reply(user_message, TextReplyContent("приветы для котиков"))
    assert actual == expected


def test_affirmative_conversion(handler):
    user_message = make_message("недобрал")
    actual = handler.handle(Update(0, user_message), None)
    expected = Reply(user_message, TextReplyContent("добери себе котика"))
    assert actual == expected


def make_message(text: str) -> Message:
    return Message(0, datetime.datetime.now(), Chat(0, "test"), text=text)


@define
class MessageBuilder:
    _text: str

    _message_id: int = field(default=0)
    _chat: Chat = field(default=Chat(0, "test"))
    _from_user: Optional[User] = field(default=None)
    _reply_to_message: Optional[Message] = field(default=None)

    def message_id(self, message_id: int) -> "MessageBuilder":
        self._message_id = message_id
        return self

    def chat(self, chat: Chat) -> "MessageBuilder":
        self._chat = chat
        return self

    def from_user(self, from_user: User) -> "MessageBuilder":
        self._from_user = from_user
        return self

    def reply_to_message(self, reply_to_message: Message) -> "MessageBuilder":
        self._reply_to_message = reply_to_message
        return self

    def build(self) -> Message:
        return Message(
            self._message_id,
            datetime.datetime.now(),
            self._chat,
            self._from_user,
            text=self._text,
            reply_to_message=self._reply_to_message
        )
