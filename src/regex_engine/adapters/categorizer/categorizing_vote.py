from regex_engine.domain.enums import Category
from regex_engine.adapters.parser.agent_ingredient_parser.parsing_vote import get_most_occurred_value
from regex_engine.application.dto import CategorizedIngredient


def choose_proper_category(ingredients:list[CategorizedIngredient]) ->Category:
    if not ingredients:
        raise ValueError("No categorized ingredients provided")

    categories = [ingredient.category for ingredient in ingredients]

    return get_most_occurred_value(categories)

