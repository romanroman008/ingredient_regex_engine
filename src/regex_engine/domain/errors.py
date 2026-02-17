class NameNotDetectedError(Exception):
    """Raised when a name cannot be detected."""
    def __init__(self, *, ingredient:str) -> None:
        self.ingredient = ingredient
        super().__init__("Name could not be detected")