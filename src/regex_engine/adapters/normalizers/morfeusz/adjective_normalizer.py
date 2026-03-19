from typing import Optional

from morfeusz2 import Morfeusz

from regex_engine.src.regex_engine.adapters.normalizers.morfeusz.ingredient_name import get_lemma, is_negative
from regex_engine.src.regex_engine.adapters.normalizers.morfeusz.morfeusz_utils import calculate_elements, \
    get_first_adjective_analysis, extract_gradation, extract_cases, extract_numbers, get_surface, extract_genders, \
    extract_sentence_parts
from regex_engine.src.regex_engine.domain.models.grammar import GrammaticalCase, GrammaticalNumber, GrammaticalGender, \
    SentencePart



class MorfeuszAdjectiveNormalizer:
    def __init__(self, morfeusz:Morfeusz):
        self.morfeusz = morfeusz



    async def stem(self, adjective:str):
        phrase_analysis = self.morfeusz.analyse(adjective)

        if calculate_elements(phrase_analysis) > 1:
            raise ValueError("Only one adjective can be stemmed")

        adjective = get_first_adjective_analysis(phrase_analysis)


        nominative = self.inflect_adjective_for_given_case_gender_number(adjective,
                                                                         GrammaticalNumber.SINGULAR,
                                                                         GrammaticalGender.MASC_INANIMATE,
                                                                         GrammaticalCase.NOMINATIVE)

        if nominative:
            return get_surface(nominative)

        return get_lemma(nominative)


    def inflect_adjective_for_given_case_gender_number(self, adjective:tuple, number:GrammaticalNumber,
                                                       gender:GrammaticalGender, case:GrammaticalCase) -> Optional[tuple]:
        variants = self.morfeusz.generate(get_lemma(adjective))

        adj_degree = extract_gradation(adjective)
        is_adj_negative = is_negative(adjective)

        for variant in variants:
            numbered_variant = (adjective[0], adjective[1], variant)

            if extract_sentence_parts(numbered_variant) not in (SentencePart.ADJECTIVE.value, SentencePart.PASSIVE_ADJECTIVAL_PARTICIPLE.value):
                continue

            var_cases = set(extract_cases(numbered_variant))
            var_numbers = set(extract_numbers(numbered_variant))
            var_genders = set(extract_genders(numbered_variant))
            var_degree = extract_gradation(numbered_variant)
            var_negative = is_negative(numbered_variant)

            if (number in var_numbers and
                    case in var_cases and
                    gender in var_genders and
                    adj_degree == var_degree and
                    is_adj_negative == var_negative
            ):
                return numbered_variant

        return None


    async def inflect(self, stem:str):
        phrase_analysis = self.morfeusz.analyse(stem)

        if calculate_elements(phrase_analysis) > 1:
            raise ValueError("Only one adjective can be inflected")

        adjective = get_first_adjective_analysis(phrase_analysis)


        cases_variations = (
            (GrammaticalNumber.SINGULAR, GrammaticalCase.NOMINATIVE),
            (GrammaticalNumber.SINGULAR, GrammaticalCase.GENITIVE),
            (GrammaticalNumber.SINGULAR, GrammaticalCase.ACCUSATIVE),
            (GrammaticalNumber.SINGULAR, GrammaticalCase.INSTRUMENTAL),
            (GrammaticalNumber.PLURAL, GrammaticalCase.NOMINATIVE),
            (GrammaticalNumber.PLURAL, GrammaticalCase.GENITIVE),
            (GrammaticalNumber.PLURAL, GrammaticalCase.INSTRUMENTAL),
        )

        genders = (
            GrammaticalGender.MASC_INANIMATE,
            GrammaticalGender.FEMININE,
            GrammaticalGender.NEUTER
        )
        result = []

        for gender in genders:
            for number, case in cases_variations:
                inflected = self.inflect_adjective_for_given_case_gender_number( adjective,
                                                                         number, gender, case)
                result.append(get_surface(inflected))

        return list(set(result))


