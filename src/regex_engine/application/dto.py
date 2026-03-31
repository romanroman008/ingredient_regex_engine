

from pydantic import BaseModel

from regex_engine.domain.enums import Category
from regex_engine.domain.models.grammar import GradationDegree, GrammaticalCase
from regex_engine.domain.models.grammar import SentencePart, GrammaticalNumber, GrammaticalGender


class ParsedIngredient(BaseModel):
    raw_input:str
    amount:float
    unit_size:str
    unit:str
    condition:str
    name:str
    extra:str


class CategorizedIngredient(BaseModel):
    category: Category
    name: str
    description: str
    reason: str


from dataclasses import dataclass, field
from typing import Optional

@dataclass(slots=True, frozen=True, kw_only=True)
class BaseWord:
    lemma: str
    surface: str
    part: SentencePart
    is_negation:bool = False
    is_pluralia_tantum:bool = False
    number: frozenset[GrammaticalNumber] = field(default_factory=frozenset)
    case: frozenset[GrammaticalCase] = field(default_factory=frozenset)
    gender: frozenset[GrammaticalGender] = field(default_factory=frozenset)
    degree: Optional[GradationDegree] = None
    annotations: tuple[str] = field(default_factory=tuple)


    def __post_init__(self) -> None:
        object.__setattr__(self, "number", frozenset(self.number))
        object.__setattr__(self, "case", frozenset(self.case))
        object.__setattr__(self, "gender", frozenset(self.gender))
        object.__setattr__(self, "annotations", tuple(self.annotations))

    @classmethod
    def _split_tag(cls, value: str, index: int) -> list[str]:
        parts = value.split(":")
        if index >= len(parts):
            return []
        return parts[index].split(".")

    @classmethod
    def _to_part(cls, tag: str) -> SentencePart:
        try:
            part = SentencePart(tag)
        except ValueError:
            part = SentencePart.UNKNOWN
        return part





@dataclass(slots=True, frozen=True)
class WordAnalysis(BaseWord):
    position: int

    @classmethod
    def _build(
        cls,
        position: int,
        lemma: str,
        surface: str,
        part: SentencePart,
        is_negation: bool = False,
        is_pluralia_tantum = False,
        number: Optional[set[GrammaticalNumber]] = None,
        case: Optional[set[GrammaticalCase]] = None,
        gender: Optional[set[GrammaticalGender]] = None,
        degree: Optional[GradationDegree] = None,
        annotations: Optional[list[str]] = None,
    ) -> "WordAnalysis":
        return cls(
            position=position,
            lemma=lemma,
            surface=surface,
            part=part,
            is_negation=is_negation,
            is_pluralia_tantum=is_pluralia_tantum,
            number=number or frozenset(),
            case=case or frozenset(),
            gender=gender or frozenset(),
            degree=degree,
            annotations=annotations or tuple(),
        )


    @classmethod
    def from_tuple(cls, analysis: tuple) -> "WordAnalysis":
        position, _, data = analysis
        surface, lemma, morph_tag, _, annotations = data

        tags = morph_tag.split(":")
        part = cls._to_part(tags[0])

        base = {
            "position": position,
            "lemma": lemma,
            "surface": surface,
            "part": part,
            "annotations": annotations,
        }

        common_inflected_parts = {
            SentencePart.NOUN,
            SentencePart.ADJECTIVE,
            SentencePart.PASSIVE_ADJECTIVAL_PARTICIPLE,
            SentencePart.ACTIVE_PARTICIPLE,
        }

        if part in common_inflected_parts:
            base["number"] = set(cls._split_tag(morph_tag, 1))
            base["case"] = set(cls._split_tag(morph_tag, 2))
            base["gender"] = set(cls._split_tag(morph_tag, 3))

        if part in (SentencePart.PASSIVE_ADJECTIVAL_PARTICIPLE, SentencePart.ACTIVE_PARTICIPLE):
            base["is_negation"] = "neg" in tags

        if part is SentencePart.NOUN:
            base["is_pluralia_tantum"] = "pt" in tags

        if part is SentencePart.ADJECTIVE:
            degree_values = cls._split_tag(morph_tag, 4)
            base["degree"] = GradationDegree(degree_values[0]) if degree_values else None

        return cls._build(**base)


@dataclass(slots=True, frozen=True)
class GeneratedWord(BaseWord):
    @classmethod
    def _build(
            cls,
            lemma: str,
            surface: str,
            part: SentencePart,
            is_negation:bool = False,
            is_pluralia_tantum=False,
            number: Optional[set[GrammaticalNumber]] = None,
            case: Optional[set[GrammaticalCase]] = None,
            gender: Optional[set[GrammaticalGender]] = None,
            degree: Optional[GradationDegree] = None,
            annotations: Optional[list[str]] = None,
    ) -> "GeneratedWord":
        return cls(
            lemma=lemma,
            surface=surface,
            part=part,
            is_negation=is_negation,
            is_pluralia_tantum=is_pluralia_tantum,
            number=number or frozenset(),
            case=case or frozenset(),
            gender=gender or frozenset(),
            degree=degree,
            annotations=annotations or tuple(),
        )

    @classmethod
    def from_tuple(cls, analysis: tuple) -> "GeneratedWord":
        surface, lemma, morph_tag, _, annotations = analysis

        tags = morph_tag.split(":")

        part = cls._to_part(tags[0])

        base = {
            "surface": surface,
            "lemma": lemma,
            "part": part,
            "annotations": annotations,
        }

        common_inflected_parts = {
            SentencePart.NOUN,
            SentencePart.ADJECTIVE,
            SentencePart.PASSIVE_ADJECTIVAL_PARTICIPLE,
            SentencePart.ACTIVE_PARTICIPLE,
        }

        if part in common_inflected_parts:
            base["number"] = set(cls._split_tag(morph_tag, 1))
            base["case"] = set(cls._split_tag(morph_tag, 2))
            base["gender"] = set(cls._split_tag(morph_tag, 3))

        if part in (SentencePart.PASSIVE_ADJECTIVAL_PARTICIPLE, SentencePart.ACTIVE_PARTICIPLE):
            base["is_negation"] = "neg" in tags

        if part is SentencePart.NOUN:
            base["is_pluralia_tantum"] = "pt" in tags

        if part is SentencePart.ADJECTIVE:
            degree_values = cls._split_tag(morph_tag, 4)
            base["degree"] = GradationDegree(degree_values[0]) if degree_values else None

        return cls._build(**base)


@dataclass(slots=True)
class PositionedWord:
    position: int
    word: BaseWord



@dataclass(frozen=True)
class AnalysedPhrase:
    subject:PositionedWord
    phrase: dict[int, str]
    dependent_noun:Optional[PositionedWord] = None
    subject_adjectives:list[PositionedWord] = field(default_factory=list)
    dependent_noun_adjectives:list[PositionedWord] = field(default_factory=list)











