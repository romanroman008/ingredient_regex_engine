from typing import Sequence

from morfeusz2 import Morfeusz

from regex_engine.src.regex_engine.adapters.normalizers.morfeusz.ingredient_name import extract_tags, get_lemma
from regex_engine.src.regex_engine.adapters.normalizers.morfeusz.morfeusz_utils import get_index, \
    extract_sentence_parts, is_noun_cooking_related, extract_numbers, extract_cases, get_surface
from regex_engine.src.regex_engine.domain.models.grammar import SentencePart, GrammaticalNumber, GrammaticalCase


def is_punctuation(analysis:tuple) -> bool:
    tags = extract_tags(analysis)
    return "interp" in tags

def calculate_non_punctuations(phrase_analysis:Sequence[tuple]) -> int:
    indexes = set()
    count = 0
    for analysis in phrase_analysis:
        index = get_index(analysis)

        if index in indexes:
            continue

        indexes.add(index)
        if not is_punctuation(analysis):
            count += 1

    return count


def filter_noun_variations(phrase_analysis:Sequence[tuple]) -> list[tuple]:
    result = []
    for analysis in phrase_analysis:
        if extract_sentence_parts(analysis) == SentencePart.NOUN.value:
            if is_noun_cooking_related(analysis):
                result.append(analysis)

    return result


class MorfeuszUnitNormalizer:
    def __init__(self, morfeusz:Morfeusz):
        self.morfeusz = morfeusz


    async def stem(self, unit:str) -> str:
        phrase_analysis = self.morfeusz.analyse(unit)
        count = calculate_non_punctuations(phrase_analysis)

        if count > 1:
            raise ValueError("Unit name has multiple words")

        unit_variations = filter_noun_variations(phrase_analysis)

        return get_lemma(unit_variations[0])




    async def inflect(self, stem:str) -> list[str]:
        variations = self.morfeusz.generate(stem)

        cases_variations = (
            (GrammaticalNumber.SINGULAR, GrammaticalCase.NOMINATIVE),
            (GrammaticalNumber.SINGULAR, GrammaticalCase.GENITIVE),
            (GrammaticalNumber.SINGULAR, GrammaticalCase.ACCUSATIVE),
            (GrammaticalNumber.SINGULAR, GrammaticalCase.INSTRUMENTAL),
            (GrammaticalNumber.PLURAL, GrammaticalCase.NOMINATIVE),
            (GrammaticalNumber.PLURAL, GrammaticalCase.GENITIVE),
            (GrammaticalNumber.PLURAL, GrammaticalCase.INSTRUMENTAL),
        )

        results = []

        for number, case in cases_variations:
            for variation in variations:
                part = extract_sentence_parts((0,0,variation))
                if part != SentencePart.NOUN.value:
                    continue

                unit_case = extract_cases((0,0,variation))
                unit_number = extract_numbers((0,0,variation))



                if (case in unit_case and
                    number in unit_number):

                    results.append(get_surface((0,0,variation)))

        return results


