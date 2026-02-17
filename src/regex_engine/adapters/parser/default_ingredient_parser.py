from agents import Agent, Runner, trace
import asyncio

from regex_engine.src.regex_engine.adapters.models import ParsedIngredient

parser_prompt = """
Jesteś parserem składników. Twoim zadaniem jest ustandaryzowanie części zdań opisujących składnik do odpowiednich kategorii:
AMOUNT - ilość składnika (1, 3, kilka, połowa, etc) 
UNIT_ADJECTIVE - przymiotnik jednostki (duża, niewielka, około) 
UNIT - jednostka ilości składnika (łyżka, gram, g, paczka, listek, etc)
CONDITION - stan składnika, do którego ma doprowadzić go kucharz (posiekany, gotowanych, schłodzonego)
NAME - pełna nazwa składnika, powinna zawierać też stan produktu, jaki zapewniony jest przez sprzedawcę (suszone pomidory, czerwona fasola, wędzonego boczku)
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
    "name": "musztardy dijon"
}
INPUT:
"500 ml bulionu jarzynowego"
OUTPUT:
{
    "full_input": "500 ml bulionu jarzynowego",
    "amount": 500,
    "unit_adjective": "",
    "unit": "ml",
    "condition": "",
    "name": "bulionu jarzynowego"
}
INPUT:
"150 g masła, schłodzonego"
OUTPUT:
{
    "full_input": "150 g masła, schłodzonego",
    "amount": 150,
    "unit_adjective": "",
    "unit": "g",
    "condition": "schłodzonego",
    "name": "masła"
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
    "name": "cukru pudru"
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
    "name": "skórka starta z pomarańczy"
}
"""

parser_agent = Agent(
    name = "parser",
    instructions=parser_prompt,
    model="gpt-4o-mini",
    output_type=ParsedIngredient,
)


class AgentIngredientParser:
    async def parse(self, ingredient:str) -> ParsedIngredient:
        with trace(f"Parser {ingredient}"):
            result = await asyncio.wait_for(
                Runner.run(parser_agent, ingredient),
                timeout=20
            )
        return result.final_output
