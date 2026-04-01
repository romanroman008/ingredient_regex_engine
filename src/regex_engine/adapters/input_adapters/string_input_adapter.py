from collections import defaultdict, Counter

from regex_engine.domain.models.ingredient_record import IngredientRecord
from regex_engine.ports.token_normalizer import TokenNormalizer


class StringInputAdapter:
    """
    If input is string instance it separates the elements by a newline character.
    """
    def supports(self, data:Any) -> bool:
       if isinstance(data, str):
           return True

       if isinstance(data, list) and all(isinstance(x, str) for x in data):
           return True

       return False

    def to_records(self, data:Any) -> list[IngredientRecord]:
        if isinstance(data, str):
            lines = [
                line.strip()
                for line in data.splitlines()
                if line.strip()
            ]

            counter = Counter(lines)

            return [
                IngredientRecord(name=name, count=count)
                    for name, count in counter.items()
            ]

        if isinstance(data, list and all(isinstance(x, str) for x in data)):
            counter = Counter(data)

            return [
                IngredientRecord(name=name, count=count)
                for name, count in counter.items()
            ]

        return []

