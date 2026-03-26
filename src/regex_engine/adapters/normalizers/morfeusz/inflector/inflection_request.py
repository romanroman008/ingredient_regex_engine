from dataclasses import dataclass

from regex_engine.src.regex_engine.domain.models.grammar import GrammaticalNumber, GrammaticalCase, GrammaticalGender


@dataclass(frozen=True, slots=True)
class InflectionRequest:
    number: GrammaticalNumber
    case: GrammaticalCase
    gender: GrammaticalGender = None

    def __post_init__(self):
        if isinstance(self.gender, (set, frozenset)):
            if len(self.gender) == 1:
                object.__setattr__(self, "gender", next(iter(self.gender)))
            elif len(self.gender) == 0:
                object.__setattr__(self, "gender", None)
            else:
                raise ValueError(f"Ambiguous gender: {self.gender}")

        elif self.gender is not None and not isinstance(self.gender, GrammaticalGender):
            raise TypeError(f"Invalid gender type: {type(self.gender)}")