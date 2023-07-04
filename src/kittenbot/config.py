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


class BotConfig(Config):
    token: str = field("token")
    probability: float = field("probability", default=0.05, caster=to_float)
    agree_probability: float = field("agree_probability", default=0.7, caster=to_float)
    test_group_ids: List[int] = field("test_group_ids", default=[], caster=ToListMapCaster(to_list, to_int))
    admin_user_ids: List[int] = field("admin_user_ids", default=[], caster=ToListMapCaster(to_list, to_int))
    bot_names: List[str] = field("bot_names", default=[], caster=to_list)
    noun_template: Template = field("noun_template", default=Template("$subj для котиков"), caster=ToTemplateCaster())
