class NameNotDetectedError(Exception):
    """Raised when a name cannot be detected."""
    def __init__(self, *, ingredient:str) -> None:
        self.ingredient = ingredient
        super().__init__("Name could not be detected")


class AmbiguousParsingError(Exception):
    """Raised when multiple equally frequent parsing results are found."""

class IngredientParsingError(Exception):
    """Raised when ingredient cannot be parsed."""