import asyncio
from pathlib import Path

from regex_engine import EngineConfig, create_engine, ResolvedIngredient
from regex_engine.bootstrap.bootstrap import create_ingredient_regex_engine
from regex_engine.config import AgentConfig
from regex_engine.ports.regex_registry import RegexRegistryReader
from settings import configure_logging

data = """
4 jajka kurki zielononóżki
2 chleby
2 śmietanki kremówki
mąka pszenna typu 2
sól i pieprz
pieprz
20 g masła 
2 i 1/2 kostki masła
5 dużych winogron
3 paczki pomidorów malinowych
"""
d = """
20 g masła 
5 kg ziemniaków
"""


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

config = EngineConfig(
    output_dir= Path("C:\\Users\\roman\\Desktop\\dre"),
    categorizer=AgentConfig(),
    parser=AgentConfig(),
)

def print_registry(registry:RegexRegistryReader):
    print(f"Registry: {registry.kind.name}")
    for entry in registry.get_all():
        print(f"stem : {entry.stem}")
        print(f"variants: {entry.variants}")
        print(f"regex: {entry.pattern.pattern}")
        print("---------------------------------")

def print_resolved_ingredients(ingredients:list[ResolvedIngredient]):
    for ingredient in ingredients:
        print(f"ingredient: {ingredient.name}")
        print(ingredient)


def main():
    engine = asyncio.run(create_engine(config))
    asyncio.run(engine.learn("""    
    2 duże łyżki ciepłego mleka
    1 szklanka wody
    3 jajka
    5 czubatych łyżek śmietany
    1 i 1/3 słoika dżemu"""
                             ))
    print_resolved_ingredients(engine.recognize_ingredients(data))
    #asyncio.run(engine.categorize_registries())
    engine.save_registries()
    #engine.save_categories()






if __name__ == '__main__':
    configure_logging()
    main()

