import json
from typing import Optional, Any

from pymorphy3 import MorphAnalyzer
from pymorphy3.tagset import OpencorporaTag
from pymorphy3.units import DictionaryAnalyzer
from telegram import Update
from telegram.ext import ContextTypes

from kittenbot.actions import Action, Reply, TextReplyContent
from kittenbot.types import HandlerFunc


def parse_handler(morph_analyzer: MorphAnalyzer) -> HandlerFunc:
    def _handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[Action]:
        if not update.message or not update.message.text:
            return None
        words = update.message.text.split(" ")[1:]
        parsed = map(morph_analyzer.parse, words)
        text = "\n".join([
            f"{word}: {json.dumps(parse, ensure_ascii=False, indent=4, cls=Encoder)}"
            for word, parse in zip(words, parsed)
        ])
        return Reply(update.message, TextReplyContent(text))
    return _handle


def inflect_handler(morph_analyzer: MorphAnalyzer) -> HandlerFunc:
    def _handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[Action]:
        if not update.message or not update.message.text:
            return None
        command_args = update.message.text.split(" ")[1:]
        word = command_args[0]
        lexemes = set(command_args[1:])
        parsed = morph_analyzer.parse(word)
        text = "\n".join([
            f"{p.inflect(lexemes).word}" for p in parsed
        ])
        return Reply(update.message, TextReplyContent(text))
    return _handle


class Encoder(json.JSONEncoder):
    def default(self, o: Any) -> str:
        if isinstance(o, OpencorporaTag):
            return super().encode(list(o.grammemes))
        if isinstance(o, DictionaryAnalyzer):
            return super().encode("<DictionaryAnalyzer>")
        return super().default(o)
