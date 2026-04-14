import asyncio

from agents import Agent, Runner, trace


from regex_engine.application.dto.agent.parsed_ingredient import ParsedIngredient

PARSER_PROMPT = """
Jesteś parserem składników. Twoim zadaniem jest ustandaryzowanie części zdań opisujących składnik do odpowiednich kategorii:
AMOUNT - ilość składnika (1, 3, kilka, połowa, etc)
UNIT_ADJECTIVE - przymiotnik jednostki (duża, niewielka, około)
UNIT - jednostka ilości składnika (łyżka, gram, g, paczka, listek, etc)
CONDITION - stan składnika, do którego ma doprowadzić go kucharz (posiekany, gotowanych, schłodzonego)
NAME - pełna nazwa składnika, powinna zawierać też stan produktu, jaki zapewniony jest przez sprzedawcę (suszone pomidory, czerwona fasola, wędzonego boczku)
EXTRA - dodatkowe informacje znajdujące się w nawiasie
Jeśli nie widzisz wyraźnej jednostki typu: gram, łyżeczka, etc. zostaw ją pustą
Zwróć tylko i wyłącznie poprawny JSON.
Przykłady:
INPUT:
"1 łyżeczka musztardy dijon"
OUTPUT:
{
    "full_input": "1 łyżeczka musztardy dijon",
    "amount": 1,
    "unit_adjective": "",
    "unit": "łyżeczka",
    "condition": "",
    "name": "musztardy dijon",
    "extra": ""
}
INPUT:
"500 ml bulionu jarzynowego"
OUTPUT:
{
    "full_input": "500 ml bulionu jarzynowego (lub wołowego)",
    "amount": 500,
    "unit_adjective": "",
    "unit": "ml",
    "condition": "",
    "name": "bulionu jarzynowego",
    "extra": "lub wołowego"
}
INPUT:
"150 g masła, schłodzonego"
OUTPUT:
{
    "full_input": "150 g masła, schłodzonego (albo 200 g margaryny)",
    "amount": 150,
    "unit_adjective": "",
    "unit": "g",
    "condition": "schłodzonego",
    "name": "masła",
    "extra": "albo 200 g margaryny"
}
INPUT:
"ok. 2/3 szklanki cukru pudru"
OUTPUT:
{
    "full_input": "ok. 2/3 szklanki cukru pudru",
    "amount": 0.6666667,
    "unit_adjective": "ok.",
    "unit": "szklanki",
    "condition": "",
    "name": "cukru pudru",
    "extra": ""
}
INPUT:
"skórka starta z 1 pomarańczy"
OUTPUT:
{
    "full_input": "skórka starta z 1 pomarańczy",
    "amount": 1,
    "unit_adjective": "",
    "unit": "",
    "condition": "",
    "name": "skórka starta z pomarańczy",
    "extra": ""
}
INPUT:
"kawałek mango"
OUTPUT:
{
    "full_input": "kawałek mango",
    "amount": 1,
    "unit_adjective": "",
    "unit": "kawałek",
    "condition": "",
    "name": "mango",
    "extra": ""
}
INPUT:
"śmietanka kremówka"
OUTPUT:
{
    "full_input": "śmietanka kremówka",
    "amount": 1,
    "unit_adjective": "",
    "unit": "",
    "condition": "",
    "name": "śmietanka kremówka",
    "extra": ""
}
"""


def build_parser_agent() -> Agent:
    return Agent(
        name="parser",
        instructions=PARSER_PROMPT,
        model="gpt-4o-mini",
        output_type=ParsedIngredient,
    )


class AgentParserClient:
    def __init__(self, agent: Agent | None = None, timeout: int = 20):
        self._agent = agent or build_parser_agent()
        self._timeout = timeout

    async def parse(self, ingredient: str, instance: int) -> ParsedIngredient:
        with trace(f"Parser: {ingredient}, instance: {instance}"):
            result = await asyncio.wait_for(
                Runner.run(self._agent, ingredient),
                timeout=self._timeout,
            )
        return result.final_output