import asyncio

from regex_engine.bootstrap.bootstrap import create_ingredient_regex_engine
from settings import configure_logging

data = """
4 jajka kurki zielononóżki
2 chleby
2 śmietanki kremówki
mąka pszenna typu 2
sól i pieprz
pieprz
20 g. masła 
"""
d = """
20 g masła 
5 kg ziemniaków
"""


def main():
    print("Welcome to Inflector")
    configure_logging()
    regex_engine = create_ingredient_regex_engine()
    asyncio.run(regex_engine.process(d))
    regex_engine.save_registries()

def categorize():
    configure_logging()
    regex_engine = create_ingredient_regex_engine()
    asyncio.run(regex_engine.categorize())
    regex_engine.save_categories()


def save_categorized_registries():
    configure_logging()
    regex_engine = create_ingredient_regex_engine()
    regex_engine.save_registries()


def load_pandas_ingredients():
    from sqlalchemy import create_engine, text
    import pandas as pd

    engine = create_engine("postgresql+psycopg://app:hardpass@localhost:5433/diet", future=True)

    sql = text("""
    SELECT
      r.id AS recipe_id,
      x.ordinality AS ingredient_no,
      x.ingredient
    FROM scrape.recipe r
    CROSS JOIN LATERAL jsonb_array_elements_text(r.data->'ingredients') WITH ORDINALITY AS x(ingredient, ordinality)
    WHERE r.status = 200
      AND r.data ? 'ingredients'
      AND jsonb_typeof(r.data->'ingredients') = 'array';
    """)

    with engine.connect() as conn:
        data = pd.read_sql(sql, conn)

    return data


if __name__ == '__main__':
    regex_engine = create_ingredient_regex_engine()

