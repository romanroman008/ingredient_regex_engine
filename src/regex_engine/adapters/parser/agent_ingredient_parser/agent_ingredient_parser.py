import asyncio
import logging

from regex_engine.src.regex_engine.domain.errors import ParsingAttemptFailedError, AttemptFailure, \
    AmbiguousParsingError, IngredientParsingError
from regex_engine.src.regex_engine.adapters.parser.agent_ingredient_parser.agent_client import AgentParserClient
from regex_engine.src.regex_engine.application.dto import ParsedIngredient
from regex_engine.src.regex_engine.adapters.parser.agent_ingredient_parser.parsing_vote import choose_proper_parsing

logger = logging.getLogger("ingredient_parser")


class AgentIngredientParser:
    def __init__(
        self,
        ensemble_size: int = 5,
        max_retries: int = 3,
        parser_client: AgentParserClient | None = None,
    ):
        self.ensemble_size = ensemble_size
        self.max_retries = max_retries
        self.parser_client = parser_client or AgentParserClient()

    async def _parse_once(self, ingredient: str) -> ParsedIngredient:
        results = await asyncio.gather(
            *(
                self.parser_client.parse(ingredient, instance)
                for instance in range(self.ensemble_size)
            ),
            return_exceptions=True
        )
        valid_results: list[ParsedIngredient] = []
        errors: list[Exception] = []

        for result in results:
            if isinstance(result, Exception):
                errors.append(result)
            else:
                valid_results.append(result)

        for error in errors:
            logger.warning("Agent parsing call failed for %s: %s", ingredient, error)

        if not valid_results:
            raise ParsingAttemptFailedError(ingredient, errors)

        return choose_proper_parsing(ingredient, valid_results)


    async def parse(self, ingredient: str) -> ParsedIngredient:
        logger.info("Parsing ingredient %s ...", ingredient)
        failures: list[AttemptFailure] = []

        for attempt in range(1, self.max_retries + 1):
            try:
                parsed_ingredient = await self._parse_once(ingredient)
                logger.info("Successfully parsed %s", ingredient)
                return parsed_ingredient

            except (AmbiguousParsingError, ParsingAttemptFailedError) as e:
                failures.append(AttemptFailure(attempt, e))
                logger.warning(
                    "Could not parse %s. Attempt %s/%s. Retrying.",
                    ingredient,
                    attempt,
                    self.max_retries,
                )


        logger.error(
            "Could not parse %s. Reached max retries %s. Aborting.",
            ingredient,
            self.max_retries,
        )
        raise IngredientParsingError(ingredient, failures)