from typing import Iterable

from attr import define
from pymorphy3 import MorphAnalyzer
from pymorphy3.analyzer import Parse
from pymorphy3.tokenizers import simple_word_tokenize


@define
class Nlp:
    analyzer: MorphAnalyzer

    def get_nouns_from_str(self, text: str) -> Iterable[Parse]:
        return filter(self.is_noun, self.parse_str(text))

    def inflect_to_plur(self, word: Parse) -> Parse:
        return word.inflect({"plur", "nomn"})

    def get_verbs_from_str(self, text: str) -> Iterable[Parse]:
        return filter(self.is_verb, self.parse_str(text))

    def parse_str(self, text: str) -> Iterable[Parse]:
        return map(lambda w: self.analyzer.parse(w)[0], simple_word_tokenize(text))

    def is_noun(self, word: Parse) -> bool:
        return word.tag.POS == "NOUN"

    def is_verb(self, word: Parse) -> bool:
        return word.tag.POS in ("VERB", "INFN")

    def inflect_to_imperative(self, word: Parse) -> Parse:
        perf_form = word.inflect({"impr", "sing", "excl", "perf"})
        if perf_form:
            return perf_form
        imperf_form = word.inflect({"impr", "sing", "excl"})
        guessed_perf = self.analyzer.parse("за" + imperf_form.word)
        if guessed_perf:
            guessed_perf = guessed_perf[0]
        else:
            guessed_perf = None
        if guessed_perf and guessed_perf.is_known:
            return guessed_perf
        return word.inflect({"impr", "sing", "excl"})


def test_inflection():
    analyzer = MorphAnalyzer()
    nlp = Nlp(analyzer)
    word = list(nlp.get_nouns_from_str("магазинах"))[0]
    actual = nlp.inflect_to_plur(word).word
    expected = "магазины"
    assert actual == expected
