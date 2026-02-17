import re
from dataclasses import dataclass, field
from typing import Iterable


def _is_empty(word:str) -> bool:
    if len(word.strip()) == 0:
        return True
    return False


@dataclass(eq=False)
class RegexEntry:
    _stem: str
    _pattern: re.Pattern
    _variants: set[str] = field(default_factory=set)

    def __init__(self, stem:str, variants:Iterable[str]):
        if _is_empty(stem):
            raise ValueError(f"stem {stem} cannot be empty")
        self._stem = stem
        self._variants = set(variants)
        self._compile()

    @property
    def stem(self):
        return self._stem

    @property
    def variants(self):
        return self._variants

    @property
    def pattern(self):
        return self._pattern

    def contains(self, text: str) -> bool:
        return bool(self._pattern.search(text))

    def find(self, text: str) -> str | None:
        m = self._pattern.search(text)
        return m.group(0) if m else None

    def find_span(self, text:str) -> tuple[int, int] | None:
        m = self._pattern.search(text)
        return (m.start(), m.end()) if m else None


    def _compile(self) -> None:
        if not self.variants:
            self.variants.add(self.stem)

        alts = "|".join(
            re.escape(v) for v in sorted(self.variants, key=len, reverse=True)
        )

        self._pattern = re.compile(
            rf"\b(?:{alts})\b",
            re.IGNORECASE | re.UNICODE,
        )

    def add_variant(self, variant: str) -> None:
        variant = variant.strip()
        if not variant:
            return

        self.variants.add(variant)
        self.variants.add(self.stem)

        self._compile()


    def remove_variant(self, variant: str) -> None:
        variant = variant.strip()
        if not variant:
            return

        # nie pozwalamy usunąć bazy
        if variant == self.stem:
            return

        if variant not in self.variants:
            return

        self.variants.remove(variant)
        self._compile()

    def __hash__(self) -> int:
        return hash(self.stem)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, RegexEntry) and self.stem == other.stem