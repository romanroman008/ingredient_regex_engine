from dataclasses import dataclass


class NameNotDetectedError(Exception):
    """Raised when a name cannot be detected."""
    def __init__(self, *, ingredient:str) -> None:
        self.ingredient = ingredient
        super().__init__("Name could not be detected")


class AmbiguousParsingError(Exception):
    """Raised when multiple equally frequent parsing results are found."""

class ParsingAttemptFailedError(Exception):
    def __init__(self, ingredient: str, errors: list[Exception]):
        self.ingredient = ingredient
        self.errors = errors
        super().__init__(self._build_message())

    def _build_message(self) -> str:
        details = "; ".join(
            f"{type(error).__name__}: {error}" for error in self.errors
        )
        return f"All parsing attempts failed for '{self.ingredient}'. Errors: {details}"


@dataclass(frozen=True, slots=True)
class ParsingAttemptFailure:
    attempt: int
    cause: Exception


class IngredientParsingError(Exception):
    """Raised when ingredient cannot be parsed."""
    def __init__(self, ingredient:str, failures:list[ParsingAttemptFailure]):
        self.ingredient = ingredient
        self.failures = failures
        super().__init__(self._build_message())

    def _build_message(self) -> str:
        parts:list[str] = [f"Failed to parse ingredient '{self.ingredient}'"]

        for failure in self.failures:
            parts.append(
                f"attempt={failure.attempt} "
                f"error={type(failure).__name__}: {failure.cause}"
            )

        return " | ".join(parts)


class WordAnalysisParseError(ValueError):
    pass