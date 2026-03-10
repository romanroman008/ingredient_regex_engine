from agents import Agent, Runner, trace
import asyncio

name_stem_prompt = """
Jesteś odpowiedzialny za przekształcanie nazw składników do mianownika liczby pojedynczej. 
Niektóre nazwy będą złożone składające się dodatkowo z przymiotnika lub paru rzeczowników, 
wtedy w mianowniku powinien być wyraz nadrzędny, a całe wyrażenie powinno brzmieć naturalnie.
Przykłady
INPUT:
{"pęczka zielonej pietruszki"}
OUTPUT:
{"pęczek zielonej pietruszki"}
INPUT:
{"gorzkiej czekolady"}
OUTPUT:
{"gorzka czekolada"}
INPUT:
{"ziemniaków"}
OUTPUT:
{"ziemniak"}
INPUT:
{"czerwonych papryk"}
OUTPUT:
{"czerwona papryka"}
"""
name_stem_agent = Agent(
    name="stem_agent",
    instructions=name_stem_prompt,
    model="gpt-4o-mini"
)


ingredient_inflector_prompt = """
Jesteś odpowiedzialny za odmienianie nazwy składnika przez przypadki. Otrzymujesz nazwę składnika w mianowniku liczby pojedynczej.
Twoim zadaniem jest odmiana go przez siedem przypadków: 
mianownik l.p., dopełniacz l.p, biernik l.p., narzędnik l.p., mianownik l.mn., dopełniacz l.mn, narzędnik l.mn
PRZYKŁAD:
INPUT:
"gorzka czekolada"
WORKFLOW:
Mianownik l.p. kto? co? (jest) -> gorzka czekolada
Dopełniacz l.p. kogo? czego? (nie ma) -> gorzkiej czekolady
Biernik l.p. kogo? co? (widzę) -> gorzką czekoladę
Narzędnik l.p. z kim? z czym? (idę) -> gorzką czekoladą
Mianownik l.mn. kto? co? (jest) -> gorzkie czekolady
Dopełniacz l.mn. kogo? czego? (nie ma) -> gorzkich czekolad
Narzędnik l.mn. z kim? z czym? (idę) -> gorzkimi czekoladami
OUTPUT:
[
 "gorzka czekolada",
 "gorzkiej czekolady",
 "gorzką czekoladę",
 "gorzką czekoladą",
 "gorzkie czekolady",
 "gorzkich czekolad",
 "gorzkimi czekoladami"
 ]
INPUT:
"sok z cytryny"
OUTPUT:
[
 "sok z cytryny",
 "soku z cytryny",
 "sok z cytryny",
 "sokiem z cytryny",
 "soki z cytryny",
 "soków z cytryny",
 "sokami z cytryny"
]
"""


ingredient_inflector_agent = Agent(
    name="ingredient_inflector_agent",
    instructions=ingredient_inflector_prompt,
    model="gpt-4o-mini",
    output_type=list[str]
)



class AgentIngredientNameNormalizer:
    async def stem(self, word:str) -> str:
        with trace(f"Ingredient Name Stem: {word}"):
            result = await asyncio.wait_for(
                Runner.run(name_stem_agent, word),
                timeout=10
            )
            stem = result.final_output
        return stem

    async def inflect(self, stem:str):
        with trace(f"Ingredient Name Inflector: {stem}"):
            result = await asyncio.wait_for(
                Runner.run(ingredient_inflector_agent, stem),
                timeout=20
            )
        return result.final_output

