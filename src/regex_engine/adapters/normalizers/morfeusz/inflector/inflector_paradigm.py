from typing import Sequence

from regex_engine.src.regex_engine.adapters.normalizers.morfeusz.inflector.inflection_request import InflectionRequest
from regex_engine.src.regex_engine.application.dto import BaseWord, GeneratedWord

from regex_engine.src.regex_engine.domain.models.grammar import SentencePart, GrammaticalNumber, GrammaticalCase


class InflectionParadigm:
    def __init__(self, word: BaseWord, variations: Sequence[GeneratedWord]) -> None:
        self.word = word
        self.variations = list(variations)

    def inflect(self, request: InflectionRequest) -> BaseWord:
        match self.word.part:
            case SentencePart.NOUN:
                return self._inflect_noun(request.number, request.case)
            case SentencePart.ADJECTIVE:
                return self._inflect_adjective(request)
            case SentencePart.PASSIVE_ADJECTIVAL_PARTICIPLE:
                return self._inflect_passive_adjectival_participle(request)
            case _:
                raise NotImplementedError(f"Unsupported part: {self.word.part}")

    def _inflect_noun(
        self,
        number: GrammaticalNumber,
        case: GrammaticalCase,
    ) -> BaseWord:
        effective_number = (
            GrammaticalNumber.PLURAL
            if self.word.is_pluralia_tantum
            else number
        )

        for variation in self.variations:
            if case in variation.case and effective_number in variation.number:
                return variation

        raise ValueError(f"Cannot inflect word: {self.word}")

    def _inflect_adjective(self, request: InflectionRequest) -> BaseWord:
        for variation in self.variations:
            if (
                request.number in variation.number
                and request.case in variation.case
                and request.gender in variation.gender
                and self.word.degree == variation.degree
            ):
                return variation

        raise ValueError(f"Cannot inflect word: {self.word}")

    def _inflect_passive_adjectival_participle(
        self,
        request: InflectionRequest,
    ) -> BaseWord:
        for variation in self.variations:
            if (
                request.number in variation.number
                and request.case in variation.case
                and request.gender in variation.gender
                and self.word.is_negation == variation.is_negation
            ):
                return variation

        raise ValueError(f"Cannot inflect word: {self.word}")