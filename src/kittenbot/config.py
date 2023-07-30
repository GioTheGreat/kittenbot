import typing
from string import Template
from typing import List

from betterconf import field, Config
from betterconf.caster import AbstractCaster, to_list, to_float, to_int


class ToListMapCaster(AbstractCaster):
    def __init__(self, splitter: AbstractCaster, mapper: AbstractCaster):
        self.splitter = splitter
        self.mapper = mapper

    def cast(self, val: str) -> typing.Union[typing.Any, typing.NoReturn]:
        return [self.mapper.cast(item) for item in self.splitter.cast(val)]


class ToTemplateCaster(AbstractCaster):
    def cast(self, val: str) -> typing.Union[typing.Any, typing.NoReturn]:
        return Template(val)


to_template = ToTemplateCaster()
to_int_list = ToListMapCaster(to_list, to_int)


class BotConfig(Config):
    token: str = field("token")
    db_connection_string: str = field("db_connection_string", default="sqlite:///bot.sqlite")
    probability: float = field("probability", default=0.05, caster=to_float)
    agree_probability: float = field("agree_probability", default=0.7, caster=to_float)
    test_group_ids: List[int] = field("test_group_ids", default=[], caster=to_int_list)
    admin_user_ids: List[int] = field("admin_user_ids", default=[], caster=to_int_list)
    bot_names: List[str] = field("bot_names", default=[], caster=to_list)
    noun_template: Template = field("noun_template", default=Template("$subj для котиков"), caster=to_template)
    verb_template: Template = field("verb_template", default=Template("$verb себе котика"), caster=to_template)
    noun_weight: float = field("noun_weight", default=1., caster=to_float)
    verb_weight: float = field("verb_weight", default=1., caster=to_float)
    answer_by_name_probability: float = field("answer_by_name_probability", default=0.5, caster=to_float)
    reaction_stopwords: List[str] = field("reaction_stopwords", default=["есть"], caster=to_list)
