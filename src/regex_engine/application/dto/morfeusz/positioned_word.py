from dataclasses import dataclass

from regex_engine.application.dto.morfeusz.base_word import BaseWord


@dataclass(slots=True)
class PositionedWord:
    position: int
    word: BaseWord
