from agents import Agent, Runner, trace
import asyncio

adjective_stem_prompt = """
Jesteś odpowiedzialny za przekształcanie przymiotników do mianownika liczby pojedynczej, rodzaju męskiego.
Przykłady
INPUT:
{"ugotowanych"}
OUTPUT:
{"ugotowany}
INPUT:
{"pokrojone"}
OUTPUT:
{"pokrojony"}
INPUT:
{"ciepły"}
OUTPUT:
{"ciepły}
"""

adjective_stem_agent = Agent(
    name="adjective_stem_agent",
    instructions=adjective_stem_prompt,
    model="gpt-4o-mini",
)


female_adjective_inflector_prompt = """
Jesteś odpowiedzialny za odmienianie przymiotnika przez przypadki. Otrzymujesz przymiotnik w mianowniku rodzaju męskiego w liczbie pojedynczej.
Twoim zadaniem jest odmiana go przez cztery przypadki rodzaju żeńskiego: 
mianownik l.p. r.żeński, dopełniacz l.p. r.żeński., narzędnik l.p. r.żeński, mianownik l.mn. r.żeński
PRZYKŁAD:
INPUT:
ugotowany
WORKFLOW:
Mianownik l.p. r.żeński: kto? co? (jest) -> ugotowana (rzodkiewka)
Dopełniacz l.p. r.żeński: kogo? czego? (nie ma) -> ugotowanej (rzodkiewki)
Narzędnik l.p. r.żeński: z kim? z czym? (idę) -> ugotowaną (rzodkiewką)
Mianownik l.mn. r.żeński: kto? co? (jest) -> ugotowane (rzodkiewki)
Teraz zbierasz wszystkie PRZYMIOTNIKI i zwracasz ich listę.
OUTPUT: 
[
  "ugotowana",
  "ugotowanej",
  "ugotowaną",
  "ugotowane"
]
INPUT:
"zblendowany"
OUTPUT:
[
  "zblendowana",
  "zblendowanej",
  "zblendowaną",
  "zblendowaną",
  "zblendowane"
]
"""

female_adjective_inflector_agent = Agent(
    name="male_adjective_inflector_agent",
    instructions=female_adjective_inflector_prompt,
    model="gpt-4o-mini",
    output_type=list[str]
)

male_adjective_inflector_prompt = """
Jesteś odpowiedzialny za odmienianie przymiotnika przez przypadki. Otrzymujesz przymiotnik w mianowniku rodzaju męskiego w liczbie pojedynczej.
Twoim zadaniem jest odmiana go przez siedem przypadków: mianownik l.p., dopełniacz l.p., celownik l.p., narzędnik l.p, dopełniacz l.mn., narzędnik l.mn.
PRZYKŁAD:
INPUT:
ugotowany
WORKFLOW:
Mianownik l.p.: kto? co? (jest) -> ugotowany (kalafior)
Dopełniacz l.p.: kogo? czego? (nie ma) -> ugotowanego (kalafiora)
Celownik l.p.: komu? czemu? (się przyglądam) -> ugotowanemu (kalafiorowi)
Narzędnik l.p.: z kim? z czym? (idę) -> ugotowanym (kalafiorem)
Dopełniacz l.mn.: kogo? czego? (nie ma) -> ugotowanych (kalafiorów)
Narzędnik l.mn.: z kim? z czym? (idę) -> ugotowanymi (kalafiorami)
Teraz zbierasz wszystkie PRZYMIOTNIKI i zwracasz ich listę.
OUTPUT: 
[
  "ugotowany",
  "ugotowanego",
  "ugotowanemu",
  "ugotowanym",
  "ugotowanych",
  "ugotowanymi"
]
INPUT:
"zblendowany"
OUTPUT:
[
  "zblendowany",
  "zblendowanego",
  "zblendowanemu",
  "zblendowanym",
  "zblendowanych",
  "zblendowanymi"
]
"""
male_adjective_inflector_agent = Agent(
    name="male_adjective_inflector_agent",
    instructions=male_adjective_inflector_prompt,
    model="gpt-4o-mini",
    output_type=list[str]
)


class AgentAdjectiveNormalizer:
    async def stem(self, word: str) -> str:
        with trace(f"Adjective Stem: {word}"):
            result = await asyncio.wait_for(
                Runner.run(adjective_stem_agent, word),
                timeout=10
            )
        stem = result.final_output
        return stem

    async def inflect(self, stem: str) -> list[str]:
        female_task = self._inflect_female(stem)
        male_task = self._inflect_male(stem)

        female_forms, male_forms = await asyncio.gather(female_task, male_task)

        return [*female_forms, *male_forms]

    async def _inflect_female(self, stem: str):
        with trace(f"Female Adjective Inflector: {stem}"):
            result = await asyncio.wait_for(
                Runner.run(female_adjective_inflector_agent, stem),
                timeout=20
            )
        return result.final_output

    async def _inflect_male(self, stem: str):
        with trace(f"Male Adjective Inflector: {stem}"):
            result = await asyncio.wait_for(
                Runner.run(male_adjective_inflector_agent, stem),
                timeout=20
            )
        return result.final_output
