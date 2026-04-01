from collections import defaultdict
from typing import Optional, Sequence

from regex_engine.domain.enums import Category
from regex_engine.domain.models.ingredient_entry import IngredientEntry


class IngredientRegexRegistry:
    def __init__(self, entries:list[IngredientEntry]) -> None:
        self._entries:list[IngredientEntry] = entries
        self._by_stem:dict[str, IngredientEntry] = self._create_by_stem()
        self._by_category:dict[Category, list[IngredientEntry]] = self._create_by_category()

    def _create_by_stem(self) -> dict[str, IngredientEntry]:
        by_stem = {}
        for entry in self._entries:
            if entry.stem in by_stem:
                raise ValueError(f"Duplicate regex stem detected: {entry.stem}")
            by_stem[entry.stem] = entry
        return by_stem

    def _create_by_category(self) -> dict[Category, list[IngredientEntry]]:
        by_category = defaultdict(list)
        for entry in self._entries:
            by_category[entry.category].append(entry)

        return by_category

    def add_entry(self, entry: IngredientEntry) -> None:
        if entry.stem in self._by_stem:
            raise ValueError(f"Stem '{entry.stem}' already exists")

        self._entries.append(entry)
        self._by_stem[entry.stem] = entry
        self._by_category[entry.category].append(entry)

    def remove_entry(self, stem: str) -> None:
        """
        Raises:
            KeyError: If stem does not exist.
        """
        entry = self._by_stem.pop(stem)
        self._entries.remove(entry)
        self._by_category[entry.category].remove(entry)

    def add_variant(self, *, stem: str, variant: str) -> None:
        """
        Raises:
            KeyError: If stem does not exist.
        """
        entry = self._by_stem[stem]
        entry.add_variant(variant)

    def remove_variant(self, *, stem: str, variant: str) -> None:
        """
        Raises:
            KeyError: If stem does not exist.
        """
        entry = self._by_stem[stem]
        entry.remove_variant(variant)

    def match_best(self, text: str) -> Optional[IngredientEntry]:
        text = text.strip()
        if not text:
            return None

        best: Optional[IngredientEntry] = None
        best_len = -1

        for entry in self._entries:
            matching = entry.find(text)
            if not matching:
                continue

            length = len(matching[0])

            if length > best_len:
                best = entry
                best_len = length

        return best

    def swap_match(self, text: str, replacement: str) -> str:
        best: Optional[IngredientEntry] = None
        best_len = -1
        best_start = None
        best_end = None

        for entry in self._entries:
            span = entry.find_spans(text)
            if not span:
                continue

            start, end = span[0]
            length = end - start

            if length > best_len:
                best = entry
                best_len = length
                best_start = start
                best_end = end

        if best is None:
            return text

        swapped = text[:best_start] + replacement + text[best_end:]

        return self.swap_match(swapped, replacement)

    def get(self, stem: str) -> Optional[IngredientEntry]:
        return self._by_stem.get(stem)

    def get_all(self) -> Sequence[IngredientEntry]:
        return tuple(sorted(self._entries, key=lambda entry: entry.stem))

    def get_all_by_category(self) -> dict[Category, list[IngredientEntry]]:
        return {
            category: sorted(entries, key=lambda entry: entry.stem)
            for category, entries in self._by_category.items()
        }

