import pytest
from unittest.mock import AsyncMock

from regex_engine.domain.errors import AmbiguousParsingError, IngredientParsingError
from regex_engine.application.dto.agent.parsed_ingredient import ParsedIngredient

from regex_engine.adapters.parser.agent_ingredient_parser.agent_ingredient_parser import AgentIngredientParser


class TestParseOnce:
    @pytest.mark.asyncio
    async def test_should_call_parser_client_parse_ensemble_size_times(self):
        ingredient = "150 g masła, schłodzonego"
        parser = AgentIngredientParser(ensemble_size=3)

        parser.parser_client.parse = AsyncMock(
            side_effect=[
                ParsedIngredient(
                    raw_input=ingredient,
                    amount=150,
                    unit_size="",
                    unit="g",
                    condition="schłodzonego",
                    name="masła",
                    extra="",
                ),
                ParsedIngredient(
                    raw_input=ingredient,
                    amount=150,
                    unit_size="",
                    unit="g",
                    condition="schłodzonego",
                    name="masła",
                    extra="",
                ),
                ParsedIngredient(
                    raw_input=ingredient,
                    amount=200,
                    unit_size="",
                    unit="g",
                    condition="schłodzonego",
                    name="masła",
                    extra="",
                ),
            ]
        )

        result = await parser._parse_once(ingredient)

        assert result == ParsedIngredient(
            raw_input=ingredient,
            amount=150,
            unit_size="",
            unit="g",
            condition="schłodzonego",
            name="masła",
            extra="",
        )
        assert parser.parser_client.parse.await_count == 3
        parser.parser_client.parse.assert_any_await(ingredient, 0)
        parser.parser_client.parse.assert_any_await(ingredient, 1)
        parser.parser_client.parse.assert_any_await(ingredient, 2)

    @pytest.mark.asyncio
    async def test_should_raise_ambiguous_parsing_error_when_vote_is_ambiguous(self):
        ingredient = "150 g masła"
        parser = AgentIngredientParser(ensemble_size=2)

        parser.parser_client.parse = AsyncMock(
            side_effect=[
                ParsedIngredient(
                    raw_input=ingredient,
                    amount=100,
                    unit_size="",
                    unit="g",
                    condition="",
                    name="masła",
                    extra="",
                ),
                ParsedIngredient(
                    raw_input=ingredient,
                    amount=200,
                    unit_size="",
                    unit="g",
                    condition="",
                    name="masła",
                    extra="",
                ),
            ]
        )

        with pytest.raises(AmbiguousParsingError):
            await parser._parse_once(ingredient)


class TestParse:
    @pytest.mark.asyncio
    async def test_should_return_parsed_ingredient_on_first_successful_attempt(self, monkeypatch):
        ingredient = "150 g masła"
        parser = AgentIngredientParser(max_retries=3)

        expected = ParsedIngredient(
            raw_input=ingredient,
            amount=150,
            unit_size="",
            unit="g",
            condition="",
            name="masła",
            extra="",
        )

        parse_once_mock = AsyncMock(return_value=expected)
        monkeypatch.setattr(parser, "_parse_once", parse_once_mock)

        result = await parser.parse(ingredient)

        assert result == expected
        parse_once_mock.assert_awaited_once_with(ingredient)

    @pytest.mark.asyncio
    async def test_should_retry_when_ambiguous_parsing_error_occurs_and_then_return_result(self, monkeypatch):
        ingredient = "150 g masła"
        parser = AgentIngredientParser(max_retries=3)

        expected = ParsedIngredient(
            raw_input=ingredient,
            amount=150,
            unit_size="",
            unit="g",
            condition="",
            name="masła",
            extra="",
        )

        parse_once_mock = AsyncMock(
            side_effect=[
                AmbiguousParsingError("Ambiguous parsing result"),
                expected,
            ]
        )
        monkeypatch.setattr(parser, "_parse_once", parse_once_mock)

        result = await parser.parse(ingredient)

        assert result == expected
        assert parse_once_mock.await_count == 2

    @pytest.mark.asyncio
    async def test_should_raise_ingredient_parsing_error_after_max_retries(self, monkeypatch):
        ingredient = "150 g masła"
        parser = AgentIngredientParser(max_retries=3)

        parse_once_mock = AsyncMock(
            side_effect=AmbiguousParsingError("Ambiguous parsing result")
        )
        monkeypatch.setattr(parser, "_parse_once", parse_once_mock)

        with pytest.raises(
            IngredientParsingError,
            match=f"Failed to parse ingredient: {ingredient}",
        ):
            await parser.parse(ingredient)

        assert parse_once_mock.await_count == 3