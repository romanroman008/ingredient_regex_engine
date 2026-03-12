import logging
import re
import string
from typing import Iterable, Optional, Sequence

from regex_engine.src.regex_engine.domain.models.grammar import SentencePart, GrammaticalNumber, GrammaticalCase, \
    GrammaticalGender, GradationDegree
from regex_engine.src.regex_engine.ports.morfeusz import Morfeusz

logger = logging.getLogger("ingredient_name_normalizer")

def _calculate_elements(sentence:Iterable[tuple]) -> int:
    elements = set()
    for position, *_ in sentence:
        elements.add(position)
    return len(elements)

def which_part(tag:str):
    part = tag.split(":")[0]
    return SentencePart(part)


def get_index(analysis:tuple):
    return analysis[0]

def get_surface(analysis:tuple):
    return analysis[2][0]


def extract_sentence_parts(analysis:tuple) -> str:
    tags = extract_tags(analysis)
    return tags[0]

def extract_tags(analysis:tuple) -> list[str]:
    return analysis[2][2].split(":")

def extract_cases(analysis:tuple) -> list[str]:
    tags = extract_tags(analysis)
    cases = tags[2].split(".")
    return cases

def extract_genders(analysis:tuple) -> list[str]:
    tags = extract_tags(analysis)
    genders = tags[3].split(".")
    return genders

def extract_numbers(analysis:tuple) -> list[str]:
    tags = extract_tags(analysis)
    numbers = tags[1].split(".")
    return numbers

def extract_gradation(analysis: tuple) -> str | None:
    tags = extract_tags(analysis)

    if tags and tags[0] == "adj" and len(tags) > 4:
        return tags[4]

    return None

def is_pluralia_tantum(analysis: tuple) -> bool:
    tags = extract_tags(analysis)
    return "pt" in tags


def get_analysis_by_index(phrase_analysis:Iterable[tuple], index:int) -> list[tuple]:
    result = []
    for analysis in phrase_analysis:
        if analysis[0] == index:
            result.append(analysis)
    return result



def reduce_analysis_by_indexes(phrase_analysis: Iterable[tuple], indexes: Iterable[int]):
    result = []

    for analysis in phrase_analysis:
        if not analysis[0] in indexes:
            result.append(analysis)

    return result



def is_noun_personal_masculine_only(analysis:tuple):
    genders = extract_genders(analysis)
    if len(genders) == 1 and genders[0] == GrammaticalGender.MASC_PERSONAL.value:
        return True
    return False

def get_annotations(analysis:tuple):
    return analysis[2][4]

def is_noun_colloquial(analysis: tuple) -> bool:
    annotations = get_annotations(analysis)
    return 'pot.' in annotations


def is_noun_former(analysis: tuple) -> bool:
    annotations = get_annotations(analysis)
    return 'daw.' in annotations

def is_noun_inflectionally_independent(analysis:tuple) -> bool:
    annotations = get_annotations(analysis)
    return 'niezal.' in annotations

def is_noun_contemptuous(analysis:tuple) -> bool:
    annotations = get_annotations(analysis)
    return 'pogard.' in annotations



def reduce_non_food_subjects(phrase_analysis: Iterable[tuple]) -> list[tuple]:
    subject = find_first_noun(phrase_analysis)
    subject_variations = get_analysis_by_index(phrase_analysis, subject[0])

    if len(subject_variations) <= 1:
        return list(phrase_analysis)

    result = []

    for variation in subject_variations:
        if (not is_noun_personal_masculine_only(variation) and
            not is_noun_former(variation) and
            not is_noun_colloquial(variation)):
            result.append(variation)


    return result





def get_all_subject_variations(phrase_analysis:Iterable[tuple]):
    result = []
    subject = find_first_noun(phrase_analysis)

    if not subject:
        return result

    for analysis in phrase_analysis:
        if analysis[0] == subject[0]:
            result.append(analysis)

    return result




def get_left_adjective_variations(phrase_analysis:Iterable[tuple], pivot:int) -> list[tuple]:
    left_neighbour_variations = get_analysis_by_index(phrase_analysis, pivot - 1)

    if left_neighbour_variations:
        part = extract_sentence_parts(left_neighbour_variations[0])
        if part == SentencePart.ADJECTIVE.value or part == SentencePart.PASSIVE_ADJECTIVAL_PARTICIPLE:
            return left_neighbour_variations

    return []


def get_right_adjective_variations(phrase_analysis:Iterable[tuple], pivot:int) -> list[tuple]:
    right_neighbour_variations = get_analysis_by_index(phrase_analysis, pivot + 1)

    if right_neighbour_variations:
        part = extract_sentence_parts(right_neighbour_variations[0])
        if part == SentencePart.ADJECTIVE.value or part == SentencePart.PASSIVE_ADJECTIVAL_PARTICIPLE:
            return right_neighbour_variations

    return []


def get_right_noun_variations(phrase_analysis:Iterable[tuple], pivot:int) -> list[tuple]:
    right_neighbour_variations = get_analysis_by_index(phrase_analysis, pivot + 1)

    result = []

    for variation in right_neighbour_variations:
        part = extract_sentence_parts(variation)
        if (part == SentencePart.NOUN.value and
                not is_noun_personal_masculine_only(variation) and
                not is_noun_contemptuous(variation) and
                not is_noun_former(variation)
        ):
            result.append(variation)

    return result



def find_first_noun(phrase_analysis:Iterable[tuple]) -> tuple | None:
    lowest_index = (100, None)
    for analysis in phrase_analysis:
        if (extract_tags(analysis)[0] == SentencePart.NOUN and
            not is_noun_personal_masculine_only(analysis) and
            not is_noun_contemptuous(analysis) and
            not is_noun_former(analysis) and
            analysis[0] < lowest_index[0]):
            lowest_index = (get_index(analysis),analysis)

    return lowest_index[1]



def is_negative(analysis:tuple) -> bool:
    tags = extract_tags(analysis)
    if "neg" in tags:
        return True
    return False



def get_lemma(analysis:tuple):
    return analysis[2][1]


def determine_correct_noun(noun_variants: list[tuple],
                               related_adjectives: list[tuple],
                               ) -> Optional[tuple]:
    if not noun_variants:
        raise ValueError("No variants provided")

    for variant in noun_variants:
        if is_noun_inflectionally_independent(variant):
            return variant

    non_food_variants = reduce_non_food_subjects(noun_variants)
    if not non_food_variants:
        raise ValueError(f"Could not find any non-person subject for noun: {noun_variants}. Are you trying to cook people?")


    if len(non_food_variants) == 1:
        return non_food_variants[0]

    for noun in non_food_variants:
        noun_genders = set(extract_genders(noun))
        noun_cases = set(extract_cases(noun))
        noun_numbers = set(extract_numbers(noun))

        for adjective in related_adjectives:
            adj_genders = set(extract_genders(adjective))
            adj_cases = set(extract_cases(adjective))
            adj_numbers = set(extract_numbers(adjective))

            if (noun_genders & adj_genders and
                noun_cases & adj_cases and
                noun_numbers & adj_numbers):
                return noun

    return non_food_variants[0]





def swap_element(numbered_phrase: dict[int, str], element: tuple[int, str]) -> dict[int, str]:
    index, value = element
    if index not in numbered_phrase:
        raise KeyError(f"Index {index} not in phrase")

    numbered_phrase[index] = value
    return numbered_phrase





def detect_right_adjectives(phrase_analysis:Sequence[tuple], subject_index:int) -> list[tuple]:
    start = subject_index + 1
    end = phrase_analysis[-1][0] + 1
    step = 1
    return _detect_adjectives(phrase_analysis, start, end, step)



def detect_left_adjectives(phrase_analysis:Sequence[tuple], subject_index:int) -> list[tuple]:
    start = subject_index - 1
    end = -1
    step = -1
    return _detect_adjectives(phrase_analysis, start, end, step)


def _detect_adjectives(
    phrase_analysis: Sequence[tuple],
    start: int,
    stop: int,
    step: int,
) -> list[tuple]:
    result = []

    allowed_parts = {
        SentencePart.ADJECTIVE.value,
        SentencePart.PASSIVE_ADJECTIVAL_PARTICIPLE.value,
    }
    bridge_parts = {
        SentencePart.PUNCTUATION_MARK.value,
        SentencePart.CONJUNCTION.value,
    }

    for i in range(start, stop, step):
        neighbour_variations = get_analysis_by_index(phrase_analysis, i)

        parts = set()
        for variant in neighbour_variations:
            part = extract_sentence_parts(variant)
            parts.add(part)

            if part in allowed_parts:
                result.append(variant)

        if not (parts & allowed_parts or parts & bridge_parts):
            break

    return result




def detect_right_site_noun_variants(phrase_analysis:Iterable[tuple], subject_index:int) -> list[tuple]:

    right_neighbour_variants = get_analysis_by_index(phrase_analysis, subject_index + 1)

    result = []

    for variant in right_neighbour_variants:
        part = extract_sentence_parts(variant)
        if part == SentencePart.NOUN.value:
            result.append(variant)

    return result




def get_one_variant_from_each_index(phrase_analysis:list[tuple]):
    indexes = set()
    result = []

    for analysis in phrase_analysis:
        if not analysis[0] in indexes:
            indexes.add(analysis[0])
            result.append(analysis)
    return result

def determine_correct_right_noun(noun_variations:list[tuple], subject:tuple) -> tuple:
    subj_number = set(extract_numbers(subject))
    for variant in noun_variations:
        if extract_sentence_parts(variant) != SentencePart.NOUN.value:
            continue

        var_number = set(extract_numbers(variant))
        var_cases = set(extract_cases(variant))


        if (var_number & subj_number and
            GrammaticalCase.GENITIVE.value in var_cases and
            not is_noun_former(variant) and
            not is_noun_contemptuous(variant) and
            not is_noun_personal_masculine_only(variant)):
            return variant

    return noun_variations[0]


def reduce_variations_to_correct_one(phrase_analysis: Sequence[tuple]) -> list[tuple]:
    subject_variations = get_all_subject_variations(phrase_analysis)

    if not subject_variations:
        raise ValueError("No subjects detected")

    result = []

    subject_index = subject_variations[0][0]

    right_site_noun_variations = detect_right_site_noun_variants(phrase_analysis, subject_index)
    related_adjectives_variations = detect_left_adjectives(phrase_analysis, subject_variations[0][0])

    if right_site_noun_variations:
        related_adjectives_variations.extend(detect_right_adjectives(phrase_analysis, subject_index + 1))
    else:
        related_adjectives_variations.extend(detect_right_adjectives(phrase_analysis, subject_index))

    valid_subject = determine_correct_noun(subject_variations, related_adjectives_variations)

    if right_site_noun_variations:
        result.append(determine_correct_right_noun(right_site_noun_variations, valid_subject))

    unique_adjectives = get_one_variant_from_each_index(related_adjectives_variations)


    result.append(valid_subject)
    result.extend(unique_adjectives)

    return result


def split_phrase(phrase:str) -> dict[int, str]:
    tokens = re.findall(r"\w+|[^\w\s]", phrase)
    return {i: v for i, v in enumerate(tokens)}

def join_tokens(tokens: dict) -> str:
    result = []
    punct = set(string.punctuation)

    for token in tokens.values():
        if result and token not in punct:
            result.append(" ")
        result.append(token)

    return "".join(result)


class MorfeuszIngredientNameNormalizer:
    def __init__(self, morfeusz:Morfeusz):
        self.morfeusz = morfeusz
        self.numbered_phrase = {}


    def noun_to_nominative(self, noun:tuple) -> list[tuple]:
        if is_noun_inflectionally_independent(noun):
            return [noun]

        variations = self.morfeusz.generate(get_lemma(noun))
        result = []

        for variation in variations:
            variation_with_position = (noun[0], noun[1], variation)
            number = extract_numbers(variation_with_position)
            case = extract_cases(variation_with_position)
            if (GrammaticalNumber.SINGULAR.value in number and
                GrammaticalCase.NOMINATIVE in case):
                result.append(variation_with_position)

        if not result:
            for variation in variations:
                variation_with_position = (noun[0], noun[1], variation)
                number = extract_numbers(variation_with_position)
                case = extract_cases(variation_with_position)
                if (GrammaticalNumber.PLURAL.value in number and
                        GrammaticalCase.NOMINATIVE in case):
                    result.append(variation_with_position)


        return result


    def adjective_to_nominative_singular(self, adjective:tuple, gender:GrammaticalGender) -> list[tuple]:
        variations = self.morfeusz.generate(get_lemma(adjective))
        is_adj_negative = is_negative(adjective)
        adj_degree = extract_gradation(adjective)
        result = []

        for variation in variations:
            variation_with_position = (adjective[0], adjective[1], variation)
            try:
                part = extract_sentence_parts(variation_with_position)
                numbers = extract_numbers(variation_with_position)
                cases = extract_cases(variation_with_position)
                genders = extract_genders(variation_with_position)
                degree = extract_gradation(variation_with_position)
            except IndexError:
                continue
            if (GrammaticalNumber.SINGULAR.value in numbers and
                GrammaticalCase.NOMINATIVE.value in cases and
                gender in genders and
                (part == SentencePart.ADJECTIVE or part == SentencePart.PASSIVE_ADJECTIVAL_PARTICIPLE) and
                (is_negative(variation_with_position) == is_adj_negative) and
                adj_degree == degree
            ):
                result.append(variation_with_position)


        return result





    def inflect_to_nominative(self, words_to_inflect:list[tuple]) -> dict[int, str]:
        subject = find_first_noun(words_to_inflect)
        subject_gender = extract_genders(subject)[0]
        subject_index = subject[0]

        result = {}

        subject_nominatives = self.noun_to_nominative(subject)

        non_person_subjects = reduce_non_food_subjects(subject_nominatives)

        result[subject[0]] = non_person_subjects[0][2][0]

        for word in words_to_inflect:
            if word[0] == subject_index:
                continue
            part = extract_sentence_parts(word)
            if (part == SentencePart.ADJECTIVE.value or
                part == SentencePart.PASSIVE_ADJECTIVAL_PARTICIPLE.value):
                nominatives = self.adjective_to_nominative_singular(word, GrammaticalGender(subject_gender))
                result[word[0]] = nominatives[0][2][0]
            if part == SentencePart.NOUN.value:
                nominatives = self.noun_to_nominative(word)
                result[word[0]] = nominatives[0][2][0]


        return result

    def inflect_noun_for_given_case(self, noun:tuple, number:GrammaticalNumber, case:GrammaticalCase) -> Optional[tuple]:
        variants = self.morfeusz.generate(noun[2][1])

        if is_noun_inflectionally_independent(noun):
            return noun

        if is_pluralia_tantum(noun) and number == GrammaticalNumber.SINGULAR.value:
            number = GrammaticalNumber.PLURAL.value


        for variant in variants:
            numbered_variant = (noun[0], noun[1], variant)

            if extract_sentence_parts(numbered_variant) != SentencePart.NOUN.value:
                continue

            noun_case = set(extract_cases(numbered_variant))
            noun_numbers = set(extract_numbers(numbered_variant))
            if number in noun_numbers and case in noun_case:
                return numbered_variant

        return None


    def inflect_adjective_for_given_case_gender_number(self, adjective:tuple, number:GrammaticalNumber,
                                                       gender:GrammaticalGender, case:GrammaticalCase) -> Optional[tuple]:
        variants = self.morfeusz.generate(adjective[2][1])

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



    async def stem(self, phrase: str) -> str:
        phrase_analysis = self.morfeusz.analyse(phrase)

        numbered_phrase = split_phrase(phrase)

        words_to_inflect = reduce_variations_to_correct_one(phrase_analysis)

        inflected = self.inflect_to_nominative(words_to_inflect)

        for index, word in inflected.items():
            numbered_phrase[index] = inflected[index]

        return join_tokens(numbered_phrase)









    async def inflect(self, stem: str)  -> list[str]:
        phrase_analysis = self.morfeusz.analyse(stem)

        numbered_phrase = split_phrase(stem)

        words_to_inflect = reduce_variations_to_correct_one(phrase_analysis)

        cases_variations = (
            (GrammaticalNumber.SINGULAR, GrammaticalCase.NOMINATIVE),
            (GrammaticalNumber.SINGULAR, GrammaticalCase.GENITIVE),
            (GrammaticalNumber.SINGULAR, GrammaticalCase.ACCUSATIVE),
            (GrammaticalNumber.SINGULAR, GrammaticalCase.INSTRUMENTAL),
            (GrammaticalNumber.PLURAL, GrammaticalCase.NOMINATIVE),
            (GrammaticalNumber.PLURAL, GrammaticalCase.GENITIVE),
            (GrammaticalNumber.PLURAL, GrammaticalCase.INSTRUMENTAL),
            )

        subject = find_first_noun(words_to_inflect)
        subject_index = subject[0]
        subject_gender = extract_genders(subject)[0]

        result = []

        second_noun = get_right_noun_variations(phrase_analysis, subject_index)
        related_adjectives = []

        if second_noun:
            second_noun = determine_correct_right_noun(second_noun, subject)
            related_adjectives.extend(detect_right_adjectives(phrase_analysis, subject_index + 1))
        else:
            related_adjectives.extend(detect_right_adjectives(phrase_analysis, subject_index))

        related_adjectives.extend(detect_left_adjectives(phrase_analysis, subject_index))

        for number, case in cases_variations:
            inflected:dict[int, str] = {
                get_index(subject): get_surface(self.inflect_noun_for_given_case(subject, number, case))}

            if second_noun:
                inflected[get_index(second_noun)] = get_surface(self.inflect_noun_for_given_case(second_noun, number, GrammaticalCase.GENITIVE))

            for adjective in related_adjectives:
                inflected[get_index(adjective)] = get_surface(self.inflect_adjective_for_given_case_gender_number(adjective, number, GrammaticalGender(subject_gender), case))

            for index, word in inflected.items():
                numbered_phrase[index] = inflected[index]

            result.append(join_tokens(numbered_phrase))


        return result













