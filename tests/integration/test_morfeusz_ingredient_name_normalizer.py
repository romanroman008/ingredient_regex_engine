import pytest

from regex_engine.src.regex_engine.adapters.normalizers.morfeusz.ingredient_name import MorfeuszIngredientNameNormalizer
from regex_engine.src.regex_engine.ports.morfeusz import Morfeusz

pytest.importorskip("morfeusz2")

import morfeusz2

@pytest.fixture(scope="session")
def morfeusz():
    return morfeusz2.Morfeusz()

@pytest.fixture
def normalizer(morfeusz: Morfeusz):
    return MorfeuszIngredientNameNormalizer(morfeusz)



@pytest.mark.asyncio
@pytest.mark.parametrize(
    "word, expected",
    [
        ("maseł", "masło"),
        ("kakao", "kakao"),
        ("mleczka kokosowego", "mleczko kokosowe"),
        ("gałki muszkatołowej", "gałka muszkatołowa"),
        ("czekolada","czekolada"),
        ("czekolad mlecznych", "czekolada mleczna"),
        ("maseł czekoladowych z dodatkiem kakao", "masło czekoladowe z dodatkiem kakao"),
        ("chleba z masłem", "chleb z masłem"),
        ("żółtek jaj", "żółtko jaja"),
        ("śmietanek kremówek", "śmietanka kremówka")

    ]
)
async def test_stem_happy_path(normalizer, word:str, expected: str):
    result = await normalizer.stem(word)

    assert result == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "word, expected",
    [

        ("kakao", "kakao"),
        ("białek", "białko"),
        ("żółtek", "żółtko"),
        ("czekolada", "czekolada"),
        ("maseł", "masło"),
        ("drożdży", "drożdże")
    ]
)
async def test_single_word(normalizer, word: str, expected: str):
    result = await normalizer.stem(word)

    assert result == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "word, expected",
    [
        ("mleczka kokosowego", "mleczko kokosowe"),
        ("gałki muszkatołowej", "gałka muszkatołowa"),
        ("czekolad mlecznych", "czekolada mleczna"),
        ("maseł czekoladowych z dodatkiem kakao", "masło czekoladowe z dodatkiem kakao"),
        ("niesłodzonego kakao", "niesłodzone kakao")
    ]
)
async def test_noun_with_adjective(normalizer, word: str, expected: str):
    result = await normalizer.stem(word)

    assert result == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "word, expected",
    [
        ("żółtek jaj", "żółtko jaja"),
        ("śmietanek kremówek", "śmietanka kremówka"),
        ("chleba z masłem", "chleb z masłem"),
        ("kiszonych ogórków okraszonych boczkiem", "kiszony ogórek okraszony boczkiem")
    ]
)
async def test_multiple_nouns(normalizer, word: str, expected: str):
    result = await normalizer.stem(word)

    assert result == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "word, expected",
    [
        ("czarnego, suchego pieprzu", "czarny, suchy pieprz"),
        ("naturalnego, słodzonego miodu", "naturalny, niesłodzony miód")
    ]
)
async def test_punctuation_marks(normalizer, word: str, expected: str):
    result = await normalizer.stem(word)

    assert result == expected