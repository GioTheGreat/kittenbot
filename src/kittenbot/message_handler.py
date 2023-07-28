import re
from string import Template
from typing import List, Optional

from attr import define
from loguru import logger
from pymorphy3.analyzer import Parse
from telegram import Update, Message
from telegram.ext import ContextTypes

from .actions import Action, Reply, TextReplyContent, DocumentReplyContent
from .language_processing import Nlp
from .random_generator import RandomGenerator
from .resources import Resources


@define(init=False, slots=False)
class KittenMessageHandler:

    def __init__(
            self,
            random_generator: RandomGenerator,
            resources: Resources,
            nlp: Nlp,
            self_user_id: int,
            action_probability: float,
            agree_probability: float,
            test_group_ids: List[int],
            bot_names: List[str],
            noun_template: Template,
            noun_weight: float,
            verb_template: Template,
            verb_weight: float,
            answer_by_name_probability: float,
    ):
        self.random_generator = random_generator
        self.resources = resources
        self.nlp = nlp
        self.self_user_id = self_user_id
        self.action_probability = action_probability
        self.agree_probability = agree_probability
        self.test_group_ids = test_group_ids
        self.noun_template = noun_template
        self.bot_names = bot_names
        self._accusative_pattern = re.compile(noun_template.substitute(subj=r"(?P<subj>\w+)"))
        self._bot_name_pattern = re.compile(
            "(" + "|".join(name + "ы?" for name in bot_names) + ")",
            re.UNICODE | re.IGNORECASE
        )
        self.noun_weight = noun_weight
        self.verb_template = verb_template
        self.verb_weight = verb_weight
        self.demo_words = []
        self.answer_by_name_probability = answer_by_name_probability

    def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[Action]:
        return self.handle(update, context)

    def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[Action]:
        if update.message is None or update.message.text is None:
            return None
        normalized_text = self._normalize_text(update.message.text)
        if subj := self._find_subj(normalized_text):
            if (re.fullmatch(self._bot_name_pattern, subj)
                    or (subj == "ты" and self._is_reply_to_bot_message(update))):
                return self.reply_with_random_gif(update.message, "izvinis")
            else:
                checksum = abs(hash(subj))
                percent = checksum % 100 / 100
                reaction = "agree" if percent < self.agree_probability else "no_sorry"
                return self.reply_with_random_gif(update.message, reaction)
        elif self._is_reply_to_bot_message(update) and "извинись" in normalized_text:
            return self.reply_with_random_gif(update.message, "no_sorry")
        else:
            return self.react_to_random_word(update)

    def reply_with_random_gif(self, message: Message, directory: str) -> Action:
        resource = self.resources.get_random_resource(directory)
        return Reply(message, DocumentReplyContent(resource.name, resource.get_bytes()))

    def react_to_random_word(self, update: Update) -> Optional[Action]:
        if update.message.message_thread_id:
            return None
        nouns = [
            w
            for w in self.nlp.get_nouns_from_str(update.message.text)
            if not re.search(self._bot_name_pattern, w.word)
        ]
        verbs = list(self.nlp.get_transitive_verbs_from_str(update.message.text))
        if not nouns and not verbs:
            return None
        demo_word: Optional[Parse] = next(filter(lambda w: w.word in self.demo_words, nouns + verbs), None)
        if demo_word:
            reply_content = self._format_template(demo_word)
            self.demo_words.remove(demo_word.word)
            return Reply(update.message, TextReplyContent(reply_content))
        if not self._should_react_to_message(update):
            return None
        if nouns and verbs:
            noun_chance = self.random_generator.get_int(1, 100) * self.noun_weight
            verb_chance = self.random_generator.get_int(1, 100) * self.verb_weight
            if noun_chance > verb_chance:
                word = self.random_generator.choice(nouns)
            else:
                word = self.random_generator.choice(verbs)
        elif nouns:
            word = self.random_generator.choice(nouns)
        else:
            word = self.random_generator.choice(verbs)
        reply_content = self._format_template(word)
        logger.info(f"reacting with message {reply_content}")
        return Reply(update.message, TextReplyContent(reply_content))

    def _should_react_to_message(self, update: Update) -> bool:
        if update.message.chat.id in self.test_group_ids:
            return True
        if (re.search(self._bot_name_pattern, update.message.text.lower())
                and self.random_generator.get_bool(self.answer_by_name_probability)):
            return True
        if self.random_generator.get_bool(self.action_probability):
            return True
        return False

    def _format_template(self, word: Parse) -> str:
        if self.nlp.is_noun(word):
            subj_inflected = self.nlp.inflect_to_plur(word).word
            return self.noun_template.substitute(subj=subj_inflected)
        verb_inflected = self.nlp.inflect_to_imperative(word).word
        return self.verb_template.substitute(verb=verb_inflected)

    def add_demo_word(self, word: str) -> None:
        self.demo_words.append(word)

    def _normalize_text(self, text: str) -> str:
        return text.lower()

    def _is_reply_to_bot_message(self, update: Update) -> bool:
        if not update.message.reply_to_message:
            return False
        return update.message.reply_to_message.from_user.id == self.self_user_id

    def _find_subj(self, text: str) -> Optional[str]:
        match = re.search(self._accusative_pattern, text)
        if not match:
            return None
        return match.group("subj")
