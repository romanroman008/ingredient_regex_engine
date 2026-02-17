from agents import Agent, Runner, trace
import asyncio

unit_stem_prompt = """
Jesteś odpowiedzialny za przekształcanie nazw jednostek do pełnej nazwy, mianownika liczby pojedynczej.
Twoim inputem są tylko i wyłącznie nazwy jednostek kuchennych w róznych odmianach bądź napisane skrótem.
Każdy input interpretuj pod kątem bycia jednostką kuchenną.
Przykłady:
INPUT:
{"g."}
OUTPUT:
{"gram}
INPUT:
{"łyżek"}
OUTPUT:
{"łyżka"}
INPUT:
{"garść"}
OUTPUT:
{"garść"}
INPUT:
{"op."}
OUTPUT:
{"opakowanie"}
"""

unit_stem_agent = Agent(
    name="unit_stem_agent",
    instructions=unit_stem_prompt,
    model="gpt-4o-mini",
)


unit_inflector_prompt = """
Jesteś odpowiedzialny za odmienianie nazwy jednostki przez przypadki. Otrzymujesz nazwę jednostki w mianowniku liczby pojedynczej.
Twoim zadaniem jest odmiana go przez siedem przypadków: 
mianownik l.p., dopełniacz l.p, biernik l.p., narzędnik l.p., mianownik l.mn., dopełniacz l.mn, narzędnik l.mn
PRZYKŁAD:
INPUT:
"gram"
WORKFLOW:
Mianownik l.p. kto? co? (jest) -> gram (czekolady)
Dopełniacz l.p. kogo? czego? (nie ma) -> grama (czekolady)
Biernik l.p. kogo? co? (widzę) -> gram (czekolady)
Narzędnik l.p. z kim? z czym? (idę) -> gramem (czekolady)
Mianownik l.mn. kto? co? (jest) -> gramy (czekolady)
Dopełniacz l.mn. kogo? czego? (nie ma) -> gramów (czekolady)
Narzędnik l.mn. z kim? z czym? (idę) -> gramami (czekolady)
OUTPUT:
[
 "gram",
 "grama",
 "gram",
 "gramem",
 "gramy",
 "gramów",
 "gramami"
 ]
INPUT:
"opakowanie"
OUTPUT:
[
"opakowanie",
"opakowania",
"opakowanie",
"opakowaniem",
"opakowania",
"opakowań",
"opakowaniami"
]
"""

unit_inflector_agent = Agent(
    name="unit_inflector_agent",
    instructions=unit_inflector_prompt,
    model="gpt-4o-mini",
    output_type=list[str]
)


class UnitNormalizer:
    async def stem(self, unit: str) -> str:
        with trace(f"Unit Stem {unit}"):
            result = await asyncio.wait_for(
                Runner.run(unit_stem_agent, unit),
                timeout=20
            )
        return result.final_output

    async def inflect(self, stem: str):
        with trace(f"Unit Inflector: {stem}"):
            result = await asyncio.wait_for(
                Runner.run(unit_inflector_agent, stem),
                timeout=20
            )
        return result.final_output


