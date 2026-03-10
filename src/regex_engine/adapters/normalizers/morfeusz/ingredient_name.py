import logging
from typing import Iterable, Optional

from regex_engine.src.regex_engine.domain.models.grammar import Word, SentencePart, GrammaticalNumber, GrammaticalCase, \
    GrammaticalGender
from regex_engine.src.regex_engine.ports.morfeusz import Morfeusz

logger = logging.getLogger("ingredient_name_normalizer")

def _calculate_elements(sentence:Iterable[tuple]) -> int:
    elements = set()
    for position, *_ in sentence:
        elements.add(position)
    return len(elements)

def _find_first_noun(phrase_analysis:Iterable[tuple]) -> tuple | None:
    for _start, _end, (_surface, _lemma, tag, _qual, _extra) in phrase_analysis:
        if tag.startswith('subst'):
            return _start, _end, (_surface, _lemma, tag, _qual, _extra)
    return None


def which_part(tag:str):
    part = tag.split(":")[0]
    return SentencePart(part)



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



def reduce_non_food_subjects(phrase_analysis: Iterable[tuple]) -> list[tuple]:
    subject = _find_first_noun(phrase_analysis)
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
    subject = _find_first_noun(phrase_analysis)

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

    if right_neighbour_variations:
        part = extract_sentence_parts(right_neighbour_variations[0])
        if part == SentencePart.NOUN.value:
            return right_neighbour_variations

    return []




def is_negative(analysis:tuple) -> bool:
    tags = extract_tags(analysis)
    if "neg" in tags:
        return True
    return False



def get_lemma(analysis:tuple):
    return analysis[2][1]


def determine_correct_noun(noun_variants: list[tuple],
                           left_adjective_variations: list[tuple],
                           right_adjective_variations: list[tuple]
                           ) -> Optional[tuple]:

    for variant in noun_variants:
        if is_noun_inflectionally_independent(variant):
            return variant


    for adj_variation in left_adjective_variations:
        adj_genders = set(extract_genders(adj_variation))
        adj_cases = set(extract_cases(adj_variation))
        adj_numbers = set(extract_numbers(adj_variation))

        for noun_variant in noun_variants:
            noun_genders = set(extract_genders(noun_variant))
            noun_cases = set(extract_cases(noun_variant))
            noun_numbers = set(extract_numbers(noun_variant))

            if (noun_genders in adj_genders and
                noun_cases in adj_cases and
                noun_numbers in adj_numbers
            ):
                return noun_variant

    for adj_variation in right_adjective_variations:
        adj_genders = set(extract_genders(adj_variation))
        adj_cases = set(extract_cases(adj_variation))
        adj_numbers = set(extract_numbers(adj_variation))

        for noun_variant in noun_variants:
            noun_genders = set(extract_genders(noun_variant))
            noun_cases = set(extract_cases(noun_variant))
            noun_numbers = set(extract_numbers(noun_variant))

            if (noun_genders & adj_genders and
                    noun_cases & adj_cases and
                    noun_numbers & adj_numbers
            ):
                return noun_variant

    return None


def swap_element(numbered_phrase: dict[int, str], element: tuple[int, str]) -> dict[int, str]:
    index, value = element
    if index not in numbered_phrase:
        raise KeyError(f"Index {index} not in phrase")

    numbered_phrase[index] = value
    return numbered_phrase



def detect_left_adjectives(phrase_analysis:list[tuple], subject_index:int):
    adjectives = []

    left_neighbour = get_analysis_by_index(phrase_analysis, subject_index)

    for i in range(subject_index - 1, 0, -1):
        left_neighbour_variations = get_analysis_by_index(phrase_analysis, i)
        if left_neighbour:
            part = extract_sentence_parts(left_neighbour[0])
            if (part != SentencePart.ADJECTIVE.value or
                part != SentencePart.PASSIVE_ADJECTIVAL_PARTICIPLE or
                part != SentencePart.CONJUNCTION.value or
                part != SentencePart.PUNCTUATION_MARK.value):
                break
            if part == SentencePart.ADJECTIVE.value or part == SentencePart.PASSIVE_ADJECTIVAL_PARTICIPLE.value:
                adjectives.append(left_neighbour_variations)

    return adjectives




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
        result = []

        for variation in variations:
            variation_with_position = (adjective[0], adjective[1], variation)
            try:
                part = extract_sentence_parts(variation_with_position)
                numbers = extract_numbers(variation_with_position)
                cases = extract_cases(variation_with_position)
                genders = extract_genders(variation_with_position)
            except IndexError:
                continue
            if (GrammaticalNumber.SINGULAR.value in numbers and
                GrammaticalCase.NOMINATIVE.value in cases and
                gender in genders and
                part != SentencePart.ACTIVE_PARTICIPLE.value and
                    (is_negative(variation_with_position) == is_adj_negative)
            ):
                result.append(variation_with_position)


        return result






    async def stem(self, phrase:str) -> str:
        phrase_analysis = self.morfeusz.analyse(phrase)

        numbered_phrase = {i: v for i, v in enumerate(phrase.split())}

        subject_variations = get_all_subject_variations(phrase_analysis)

        if not subject_variations:
            raise ValueError(f"Could not find any subject for phrase: {phrase}")

        subject_variations = reduce_non_food_subjects(subject_variations)
        left_adjective_variations = get_left_adjective_variations(phrase_analysis, subject_variations[0][0])
        right_adjective_variations = get_right_adjective_variations(phrase_analysis, subject_variations[0][0])
        right_noun = get_right_noun_variations(phrase_analysis, subject_variations[0][0])

        valid_subject = None

        if not subject_variations:
            raise ValueError(f"Could not find any non-person subject for phrase: {phrase}. Are you trying to cook people?")

        if len(subject_variations) == 1:
            valid_subject = subject_variations[0]

        if len(subject_variations) > 1:
            valid_subject = determine_correct_noun(subject_variations, left_adjective_variations, right_adjective_variations)
            if not valid_subject:

                raise ValueError(f"Found more than one subject for phrase: {phrase} and could not determine correct one.")


        subject_gender = GrammaticalGender(extract_genders(valid_subject)[0])


        if left_adjective_variations:
            adjective_variations = self.adjective_to_nominative_singular(left_adjective_variations[0], subject_gender)
            if len(adjective_variations) > 1:
                raise ValueError(f"Found more than one adjective possibilities for phrase: %s, "
                                 f"adjective %s, "
                                 f"possibilities: %s.",
                                 phrase, left_adjective_variations[0][2][0], adjective_variations)
            numbered_phrase =swap_element(numbered_phrase, (adjective_variations[0][0], adjective_variations[0][2][0]))


        subject_nominatives = self.noun_to_nominative(valid_subject)
        if len(subject_nominatives) > 1:
            subject_nominatives = reduce_non_food_subjects(subject_nominatives)
            if len(subject_nominatives) > 1:
                raise ValueError(f"Found more than one nominative for noun: {valid_subject}.")
        numbered_phrase = swap_element(numbered_phrase, (subject_nominatives[0][0], subject_nominatives[0][2][0]))


        if right_adjective_variations:
            adjective_variations = self.adjective_to_nominative_singular(right_adjective_variations[0], subject_gender)
            if len(adjective_variations) > 1:
                raise ValueError(f"Found more than one adjective possibilities for phrase: %s, "
                                 f"adjective %s, "
                                 f"possibilities: %s.",
                                 phrase, right_adjective_variations[0][2][0], adjective_variations)
            numbered_phrase = swap_element(numbered_phrase, (adjective_variations[0][0], adjective_variations[0][2][0]))


        if right_noun:
            noun_variations = self.noun_to_nominative(right_noun[0])
            if len(noun_variations) > 1:
                raise ValueError(f"Found more than one nominative for noun: {valid_subject}.")
            numbered_phrase = swap_element(numbered_phrase, (noun_variations[0][0], noun_variations[0][2][0]))


        return " ".join(numbered_phrase.values())







    async def inflect(self, stem: str) -> list[str]:
        pass