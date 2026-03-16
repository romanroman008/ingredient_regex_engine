import pytest

from regex_engine.src.regex_engine.adapters.parser.agent_ingredient_parser.parsing_vote import get_most_occurred_value, \
    choose_proper_parsing

from regex_engine.src.regex_engine.domain.errors import AmbiguousParsingError

from regex_engine.src.regex_engine.application.dto import ParsedIngredient


class TestGetMostOccurredValue:
    def test_should_return_most_common_value_when_there_is_single_winner(self):
        values = ["g", "g", "ml"]

        result = get_most_occurred_value(values)

        assert result == "g"

    def test_should_return_empty_string_when_empty_string_is_most_common_value(self):
        values = ["", "", "g"]

        result = get_most_occurred_value(values)

        assert result == ""

    def test_should_raise_ambiguous_parsing_error_when_values_list_is_empty(self):
        with pytest.raises(AmbiguousParsingError, match="No values to choose from"):
            get_most_occurred_value([])

    def test_should_raise_ambiguous_parsing_error_when_there_is_a_tie(self):
        values = ["g", "ml"]

        with pytest.raises(AmbiguousParsingError, match="Ambiguous parsing result"):
            get_most_occurred_value(values)

    def test_should_raise_ambiguous_parsing_error_when_multiple_values_have_same_top_count(self):
        values = ["g", "ml", "g", "ml"]

        with pytest.raises(AmbiguousParsingError, match="Ambiguous parsing result"):
            get_most_occurred_value(values)



class TestChooseProperParsing:
    def test_should_return_parsed_ingredient_with_most_common_values(self):
        raw_input = "150 g masła, schłodzonego"
        ingredients = [
            ParsedIngredient(
                raw_input=raw_input,
                amount=150,
                unit_size="",
                unit="g",
                condition="schłodzonego",
                name="masła",
            ),
            ParsedIngredient(
                raw_input=raw_input,
                amount=200,
                unit_size="",
                unit="g",
                condition="schłodzonego",
                name="masła",
            ),
            ParsedIngredient(
                raw_input=raw_input,
                amount=150,
                unit_size="małe",
                unit="g",
                condition="schłodzonego",
                name="masła",
            ),
        ]

        result = choose_proper_parsing(raw_input, ingredients)

        assert result == ParsedIngredient(
            raw_input=raw_input,
            amount=150,
            unit_size="",
            unit="g",
            condition="schłodzonego",
            name="masła",
        )

    def test_should_raise_ambiguous_parsing_error_when_ingredients_list_is_empty(self):
        with pytest.raises(AmbiguousParsingError, match="No parsed ingredients provided"):
            choose_proper_parsing("150 g masła, schłodzonego", [])

    def test_should_raise_ambiguous_parsing_error_when_amount_is_ambiguous(self):
        raw_input = "x"
        ingredients = [
            ParsedIngredient(
                raw_input=raw_input,
                amount=100,
                unit_size="",
                unit="g",
                condition="",
                name="masła",
            ),
            ParsedIngredient(
                raw_input=raw_input,
                amount=200,
                unit_size="",
                unit="g",
                condition="",
                name="masła",
            ),
        ]

        with pytest.raises(AmbiguousParsingError, match="Ambiguous parsing result"):
            choose_proper_parsing(raw_input, ingredients)

    def test_should_raise_ambiguous_parsing_error_when_unit_size_is_ambiguous(self):
        raw_input = "x"
        ingredients = [
            ParsedIngredient(
                raw_input=raw_input,
                amount=100,
                unit_size="małe",
                unit="g",
                condition="",
                name="masła",
            ),
            ParsedIngredient(
                raw_input=raw_input,
                amount=100,
                unit_size="duże",
                unit="g",
                condition="",
                name="masła",
            ),
        ]

        with pytest.raises(AmbiguousParsingError, match="Ambiguous parsing result"):
            choose_proper_parsing(raw_input, ingredients)

    def test_should_raise_ambiguous_parsing_error_when_unit_is_ambiguous(self):
        raw_input = "x"
        ingredients = [
            ParsedIngredient(
                raw_input=raw_input,
                amount=100,
                unit_size="",
                unit="g",
                condition="",
                name="masła",
            ),
            ParsedIngredient(
                raw_input=raw_input,
                amount=100,
                unit_size="",
                unit="ml",
                condition="",
                name="masła",
            ),
        ]

        with pytest.raises(AmbiguousParsingError, match="Ambiguous parsing result"):
            choose_proper_parsing(raw_input, ingredients)

    def test_should_raise_ambiguous_parsing_error_when_condition_is_ambiguous(self):
        raw_input = "x"
        ingredients = [
            ParsedIngredient(
                raw_input=raw_input,
                amount=100,
                unit_size="",
                unit="g",
                condition="schłodzonego",
                name="masła",
            ),
            ParsedIngredient(
                raw_input=raw_input,
                amount=100,
                unit_size="",
                unit="g",
                condition="roztopionego",
                name="masła",
            ),
        ]

        with pytest.raises(AmbiguousParsingError, match="Ambiguous parsing result"):
            choose_proper_parsing(raw_input, ingredients)

    def test_should_raise_ambiguous_parsing_error_when_name_is_ambiguous(self):
        raw_input = "x"
        ingredients = [
            ParsedIngredient(
                raw_input=raw_input,
                amount=100,
                unit_size="",
                unit="g",
                condition="",
                name="masła",
            ),
            ParsedIngredient(
                raw_input=raw_input,
                amount=100,
                unit_size="",
                unit="g",
                condition="",
                name="margaryny",
            ),
        ]

        with pytest.raises(AmbiguousParsingError, match="Ambiguous parsing result"):
            choose_proper_parsing(raw_input, ingredients)

    def test_should_allow_empty_strings_as_valid_majority_values(self):
        raw_input = "1 pomarańcza"
        ingredients = [
            ParsedIngredient(
                raw_input=raw_input,
                amount=1,
                unit_size="",
                unit="",
                condition="",
                name="pomarańcza",
            ),
            ParsedIngredient(
                raw_input=raw_input,
                amount=1,
                unit_size="",
                unit="",
                condition="",
                name="pomarańcza",
            ),
            ParsedIngredient(
                raw_input=raw_input,
                amount=1,
                unit_size="duża",
                unit="szt",
                condition="",
                name="pomarańcza",
            ),
        ]

        result = choose_proper_parsing(raw_input, ingredients)

        assert result == ParsedIngredient(
            raw_input=raw_input,
            amount=1,
            unit_size="",
            unit="",
            condition="",
            name="pomarańcza",
        )