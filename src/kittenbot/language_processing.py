from typing import Iterable

from attr import define
from pymorphy3 import MorphAnalyzer
from pymorphy3.analyzer import Parse
from pymorphy3.tokenizers import simple_word_tokenize


@define
class Nlp:
    analyzer: MorphAnalyzer

    def get_nouns_from_str(self, text: str) -> Iterable[Parse]:
        words = map(lambda w: self.analyzer.parse(w)[0], simple_word_tokenize(text))
        return filter(lambda word: word.tag.POS == "NOUN", words)

    def inflect_to_plur(self, word: Parse) -> Parse:
        return word.inflect({"plur", "nomn"})


def test_inflection():
    analyzer = MorphAnalyzer()
    nlp = Nlp(analyzer)
    word = list(nlp.get_nouns_from_str("магазинах"))[0]
    actual = nlp.inflect_to_plur(word).word
    expected = "магазины"
    assert actual == expected
