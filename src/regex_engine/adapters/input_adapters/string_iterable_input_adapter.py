import logging
from typing import Any, Iterable, Counter


from regex_engine.domain.models.ingredient_record import IngredientRecord

logger = logging.getLogger(__name__ )

class StringIterableInputAdapter:
    def supports(self, data:Any) -> bool:
        return isinstance(data, Iterable) and not isinstance(data, (str, bytes))


    def to_records(self, data:Any) -> list[IngredientRecord]:
        if not self.supports(data):
            raise TypeError(f"Unsupported data type: {type(data).__name__}")

        counter = Counter()

        for i, item in enumerate(data):
            if not isinstance(item, str):
                logger.error(f"Invalid %s element. Unsupported data type: %s", i, type(item).__name__)
                continue
            counter[item] += 1


        return [
            IngredientRecord(name=name, count=count)
            for name, count in counter.items()
        ]
