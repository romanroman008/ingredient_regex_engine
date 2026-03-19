import logging
from typing import Iterable, Optional, Sequence

from regex_engine.src.regex_engine.application.dto import BaseWord, WordAnalysis
from regex_engine.src.regex_engine.domain.models.grammar import GrammaticalGender, SentencePart


logger = logging.getLogger(__name__)


def calculate_elements(sentence:Iterable[tuple]) -> int:
    elements = set()
    for position, *_ in sentence:
        elements.add(position)
    return len(elements)

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

def is_noun_cooking_related(analysis:tuple):
    return (not is_noun_personal_masculine_only(analysis) and
            not is_noun_colloquial(analysis) and
            not is_noun_former(analysis) and
            not is_noun_contemptuous(analysis))

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





def reduce_word_variations_to_one(
    analysis: Sequence[WordAnalysis],
    words_number: int
) -> list[WordAnalysis]:
    subject_index = find_first_noun_index(analysis)
    if subject_index < 0:
        raise ValueError("Could not find subject noun")

    subject_variations = get_word_analysis_by_index(analysis, subject_index)

    if len(subject_variations) == 1 and words_number == 1:
        return [subject_variations[0]]

    dependent_word_variations = get_dependent_noun_variations(analysis, subject_index)

    subject_span = (
        subject_index,
        subject_index + int(bool(dependent_word_variations))
    )
    related_adjectives = get_subject_related_adjectives(analysis, subject_span)

    correct_noun = determine_correct_subject(subject_variations, related_adjectives)

    reduced_adjectives = get_first_variant_from_each_index(related_adjectives)
    reduced_adjectives.append(correct_noun)

    return reduced_adjectives


def get_first_variant_from_each_index(analysis: Sequence[WordAnalysis]) -> list[WordAnalysis]:
    max_position = max(word.position for word in analysis)

    already = set()
    result = []

    for i in range(max_position + 1):
        if not i in already:
            already.add(i)
            result.append(analysis[i])

    return result




def get_word_analysis_by_index(analysis:Sequence[WordAnalysis], index:int):
    return [word for word in analysis if word.position == index]

def find_first_noun_index(analysis:Sequence[WordAnalysis]) -> int:
    sorted_analysis = sorted(analysis, key=lambda w:w.position)
    for word in sorted_analysis:
        if word.part == SentencePart.NOUN.value:
            return word.position
    return -1

def filter_non_cooking_related(analysis:Sequence[WordAnalysis]) -> list[WordAnalysis]:
    return [word for word in analysis if is_word_cooking_related(word)]

def tuples_to_word_analysis(tuples:list[tuple]) -> list[WordAnalysis]:
    return [WordAnalysis.from_tuple(t) for t in tuples]


def is_word_cooking_related(word:BaseWord) -> bool:
    return not (is_word_colloquial(word) and
                is_word_former(word) and
                is_word_abusive(word) and
                is_word_masculine_personal_only(word)
                )

def is_word_inflectionally_independent(word:BaseWord) -> bool:
    return ('niezal.' in word.annotations
            or len(word.case) == 7
            )

def is_word_former(word:BaseWord) -> bool:
    return 'daw.' in word.annotations

def is_word_colloquial(word:BaseWord) -> bool:
    return 'pot.' in word.annotations

def is_word_abusive(word:BaseWord) -> bool:
    return 'pogard.' in word.annotations

def is_word_masculine_personal_only(word:BaseWord) -> bool:
    return (
            len(word.gender) == 1
            and word.gender is GrammaticalGender.MASC_PERSONAL
            )



def get_first_adjective_analysis(phrase_analysis:Iterable[tuple]) -> Optional[tuple]:
    for analysis in phrase_analysis:
        part = extract_sentence_parts(analysis)
        if (part == SentencePart.ADJECTIVE.value or
            part == SentencePart.PASSIVE_ADJECTIVAL_PARTICIPLE.value):
            return analysis
    return None



