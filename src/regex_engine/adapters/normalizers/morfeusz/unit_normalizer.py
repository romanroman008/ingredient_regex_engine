from typing import Sequence

from morfeusz2 import Morfeusz

from regex_engine.src.regex_engine.adapters.normalizers.morfeusz.morfeusz_utils import tuples_to_generated_word

from regex_engine.src.regex_engine.adapters.normalizers.morfeusz.inflector.inflector_paradigm import InflectionParadigm
from regex_engine.src.regex_engine.application.dto import BaseWord
from regex_engine.src.regex_engine.adapters.normalizers.morfeusz.inflector.inflection_request import InflectionRequest

from regex_engine.src.regex_engine.domain.models.grammar import GrammaticalNumber, GrammaticalCase, SentencePart
from regex_engine.src.regex_engine.adapters.normalizers.morfeusz.inflector.inflector import Inflector


def _choose_first_noun(words:list[BaseWord]) -> BaseWord:
    for word in words:
        part = word.part
        if part == SentencePart.NOUN:
            return word

    raise ValueError(f"Could not find adjective or passive adjective participle in {words}")


class MorfeuszUnitNormalizer:
    def __init__(self, inflector:Inflector, morfeusz:Morfeusz):
        self._inflector = inflector
        self._morfeusz = morfeusz
        self._inflections = [
            InflectionRequest(GrammaticalNumber.SINGULAR, GrammaticalCase.NOMINATIVE),
            InflectionRequest(GrammaticalNumber.SINGULAR, GrammaticalCase.GENITIVE),
            InflectionRequest(GrammaticalNumber.SINGULAR, GrammaticalCase.ACCUSATIVE),
            InflectionRequest(GrammaticalNumber.SINGULAR, GrammaticalCase.INSTRUMENTAL),
            InflectionRequest(GrammaticalNumber.PLURAL, GrammaticalCase.NOMINATIVE),
            InflectionRequest(GrammaticalNumber.PLURAL, GrammaticalCase.GENITIVE),
            InflectionRequest(GrammaticalNumber.PLURAL, GrammaticalCase.INSTRUMENTAL),
        ]
        self._unit:BaseWord | None = None
        self._unit_inflector:InflectionParadigm | None = None


    async def stem(self, unit:str) -> str:
        self._prepare(unit)
        return self._unit_inflector.inflect(
            InflectionRequest(
                GrammaticalNumber.SINGULAR,
                GrammaticalCase.NOMINATIVE)
        ).surface


    async def inflect(self, stem:str) -> list[str]:
        self._prepare(stem)
        return [self._unit_inflector.inflect(inflection).surface for inflection in self._inflections]


    def _prepare(self, unit:str):
        converted = self._convert_to_single_base_word(unit)
        unit_word = _choose_first_noun(converted)
        self._unit = unit_word
        self._unit_inflector = self._inflector.prepare(unit_word)



    def _convert_to_single_base_word(self, unit: str) -> list[BaseWord]:
        analyse = self._morfeusz.analyse(unit)
        last_analyse_position = analyse[-1][0]
        if last_analyse_position != 0:
            raise ValueError(f"Multiple words detected {unit}")
        return tuples_to_generated_word(analyse)

