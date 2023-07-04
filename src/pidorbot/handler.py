import random

from attr import define
from pymorphy3 import MorphAnalyzer
from pymorphy3.tokenizers import simple_word_tokenize
from telegram import Update
from telegram.ext import ContextTypes

from .random_generator import BinaryRandomGenerator


@define
class PidorHandler:
    random_generator: BinaryRandomGenerator
    analyzer: MorphAnalyzer

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.message.message_thread_id:
            return
        if self.random_generator.generate() is False:
            return
        if update.message.text is None:
            return
        parsed_words = map(lambda w: self.analyzer.parse(w)[0], simple_word_tokenize(update.message.text))
        nouns = [parsed for parsed in parsed_words if parsed.tag.POS == "NOUN"]
        # nouns = [parsed
        #          for word in simple_word_tokenize(update.message.text)
        #          if (parsed := self.analyzer.parse(word)[0]).tag.POS == "NOUN"]
        pidor_thing = nouns[random.randint(0, len(nouns) - 1)]
        pidor_thing_multiple = pidor_thing.inflect({"plur"}).word
        await update.message.reply_text(f'{pidor_thing_multiple} для пидоров')
