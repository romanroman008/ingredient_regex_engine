from typing import Iterable, Optional

from regex_engine.src.regex_engine.domain.models.grammar import GrammaticalGender, SentencePart


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

def get_first_adjective_analysis(phrase_analysis:Iterable[tuple]) -> Optional[tuple]:
    for analysis in phrase_analysis:
        part = extract_sentence_parts(analysis)
        if (part == SentencePart.ADJECTIVE.value or
            part == SentencePart.PASSIVE_ADJECTIVAL_PARTICIPLE.value):
            return analysis
    return None
