import re
from string import Template
from typing import List, Optional

from attr import define
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

    def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[Action]:
        if update.message is None or update.message.text is None:
            return None
        normalized_text = self._normalize_text(update.message.text)
        if subj := self._find_subj(normalized_text):
            if ((subj in self.bot_names or subj.rstrip("ы") in self.bot_names)
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
        if (self.random_generator.get_bool(self.action_probability) is False
                and update.message.chat.id not in self.test_group_ids):
            return None
        nouns = list(self.nlp.get_nouns_from_str(update.message.text))
        if not nouns:
            return None
        subj = self.random_generator.choice(nouns)
        subj_inflected = self.nlp.inflect_to_plur(subj).word
        return Reply(update.message, TextReplyContent(self.noun_template.substitute(subj=subj_inflected)))

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
