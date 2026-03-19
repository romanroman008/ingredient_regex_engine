from typing import Counter

import pytest

from regex_engine.src.regex_engine.adapters.normalizers.morfeusz.unit_normalizer import MorfeuszUnitNormalizer

pytest.importorskip("morfeusz2")

import morfeusz2

@pytest.fixture(scope="session")
def morfeusz():
    return morfeusz2.Morfeusz()

@pytest.fixture
def normalizer(morfeusz: morfeusz2.Morfeusz):
    return MorfeuszUnitNormalizer(morfeusz)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "unit_name, expected",
    [
        ("łyżek","łyżka"),
        ("gram", "gram"),
        ("gramy", "gram"),
        ("łyżeczek", "łyżeczka"),
        ("szczypty", "szczypta"),
        ("opakowań", "opakowanie"),
        ("garści", "garść")

    ]
)
async def test_stem_inflected_units(normalizer, unit_name:str, expected:str):
    result = await normalizer.stem(unit_name)

    assert result == expected




@pytest.mark.asyncio
@pytest.mark.parametrize(
    "unit_name, expected",
    [
        ("gram",[
            "gram",
            "grama",
            "gramem",
            "gramy",
            "gramów",
            "gramami"
        ]),
        ("opakowanie", [
            "opakowanie",
            "opakowania",
            "opakowaniem",
            "opakowań",
            "opakowaniami"
        ]),
        ("paczka", [
            "paczka",
            "paczki",
            "paczkę",
            "paczką",
            "paczek",
            "paczkami"
        ]),
        ("szczypta", [
            "szczypta",
            "szczypty",
            "szczyptę",
            "szczyptą",
            "szczypt",
            "szczyptami"
        ]),
        ("mililitr", [
            "mililitr",
            "mililitra",
            "mililitrem",
            "mililitry",
            "mililitrów",
            "mililitrami"
        ]),
    ]
)
async def test_inflect_happy_path(normalizer, unit_name:str, expected:list[str]):
    result = await normalizer.inflect(unit_name)
    assert Counter(result) == Counter(expected)


