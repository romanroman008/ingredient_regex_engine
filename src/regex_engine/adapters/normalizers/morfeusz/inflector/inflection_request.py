from dataclasses import dataclass

from regex_engine.src.regex_engine.domain.models.grammar import GrammaticalNumber, GrammaticalCase, GrammaticalGender


@dataclass(frozen=True, slots=True)
class InflectionRequest:
    number: GrammaticalNumber
    case: GrammaticalCase
    gender: GrammaticalGender = None