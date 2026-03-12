from dataclasses import dataclass
from enum import StrEnum
from typing import Optional


class SentencePart(StrEnum):
    NOUN = "subst"
    PREPOSITION = "prep"
    ADJECTIVE = "adj"
    CONJUNCTION = "conj"
    ABBREVIATION = "brev"
    PASSIVE_ADJECTIVAL_PARTICIPLE = "ppas"
    ACTIVE_PARTICIPLE = "pact"
    PUNCTUATION_MARK = "interp"
    UNKNOWN = "unknown"

class GrammaticalNumber(StrEnum):
    SINGULAR = "sg"
    PLURAL = "pl"

class GradationDegree(StrEnum):
    POSITIVE = "pos"
    COMPARATIVE = "com"
    SUPERLATIVE = "sup"

class GrammaticalCase(StrEnum):
    NOMINATIVE = "nom"      # mianownik
    GENITIVE = "gen"        # dopełniacz
    DATIVE = "dat"          # celownik
    ACCUSATIVE = "acc"      # biernik
    INSTRUMENTAL = "inst"   # narzędnik
    LOCATIVE = "loc"        # miejscownik
    VOCATIVE = "voc"        # wołacz

class GrammaticalGender(StrEnum):
    MASC_PERSONAL = "m1"  # męskoosobowy
    MASC_ANIMATE = "m2"  # męskozwierzęcy
    MASC_INANIMATE = "m3"  # męskonieżywotny
    FEMININE = "f"  # żeński
    NEUTER = "n" #nijaki


