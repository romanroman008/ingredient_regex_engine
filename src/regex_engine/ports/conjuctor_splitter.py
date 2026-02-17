from typing import Protocol


class ConjunctionSplitter(Protocol):
    async def split(self, ingredients: list[str]) -> list[str]: ...
