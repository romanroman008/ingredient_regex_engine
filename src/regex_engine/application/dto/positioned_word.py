from dataclasses import dataclass

from regex_engine.application.dto.base_word import BaseWord


@dataclass(slots=True)
class PositionedWord:
    position: int
    word: BaseWord
