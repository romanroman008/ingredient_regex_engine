from enum import Enum, auto


class EnsureStatus(Enum):
    ALREADY_MATCHED = auto()
    UPDATED_EXISTING = auto()
    CREATED_NEW = auto()
    SKIPPED_EMPTY = auto()
    FAILED = auto()

class RegexKind(Enum):
    UNIT_SIZE = auto()
    UNIT = auto()
    INGREDIENT_CONDITION = auto()
    INGREDIENT_NAME = auto()
    OR_CONJUNCTIONS = auto()
    AND_CONJUNCTIONS = auto()