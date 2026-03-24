import pytest

from regex_engine.src.regex_engine.adapters.normalizers.morfeusz.phrase_analyzer import PhraseAnalyser
from regex_engine.src.regex_engine.adapters.normalizers.morfeusz.inflector.inflector import Inflector
from regex_engine.src.regex_engine.adapters.normalizers.morfeusz.ingredient_name import MorfeuszIngredientNameNormalizer


pytest.importorskip("morfeusz2")

import morfeusz2

@pytest.fixture(scope="session")
def morfeusz():
    return morfeusz2.Morfeusz()

@pytest.fixture(scope="session")
def inflector(morfeusz):
    return Inflector(morfeusz)

@pytest.fixture(scope="session")
def phrase_analyser(morfeusz):
    return PhraseAnalyser(morfeusz)

@pytest.fixture
def normalizer(inflector: Inflector, phrase_analyser: PhraseAnalyser):
    return MorfeuszIngredientNameNormalizer(inflector, phrase_analyser)



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
async def test_stem_multiple_nouns(normalizer, word: str, expected: str):
    result = await normalizer.stem(word)

    assert result == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "word, expected",
    [
        ("czarnego, suchego pieprzu", "czarny, suchy pieprz"),
        ("naturalnego, słodzonego miodu", "naturalny, słodzony miód"),
        ("niebieskich żółtek jaj gotowanych i obranych", "niebieskie żółtko jaja gotowane i obrane"),
        ("mąki kolorowej typu 2", "mąka kolorowa typu 2")
    ]
)
async def test_stem_with_punctuation_marks(normalizer, word: str, expected: str):
    result = await normalizer.stem(word)

    assert result == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "word, expected",
    [
        ("niesłodzonego kakao", "niesłodzone kakao"),
        ("niesłodzonego cukru", "niesłodzony cukier"),
        ("nieświeżych śledzi", "nieświeży śledź"),
        ("nienaturalnego jogurtu", "nienaturalny jogurt")
    ]
)
async def test_stem_with_negations(normalizer, word: str, expected: str):
    result = await normalizer.stem(word)

    assert result == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "word, expected",
    [

        ("kakao", ["kakao", "kakao", "kakao", "kakao", "kakao", "kakao", "kakao",]),
        ("białko", ["białko", "białka", "białko", "białkiem", "białka", "białek", "białkami"]),
        ("żółtko", ["żółtko", "żółtka", "żółtko", "żółtkiem", "żółtka", "żółtek", "żółtkami"]),
        ("czekolada", ["czekolada", "czekolady", "czekoladę", "czekoladą", "czekolady", "czekolad", "czekoladami"]),
        ("masło", ["masło", "masła", "masło", "masłem", "masła", "maseł", "masłami"]),
        ("drożdże", ["drożdże", "drożdży", "drożdże", "drożdżami", "drożdże", "drożdży", "drożdżami"])
    ]
)
async def test_inflect_single_ingredients_names(normalizer, word, expected: list[str]):
    result = await normalizer.inflect(word)

    assert result == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "word, expected",
    [
        ("mleczko kokosowe",[
            "mleczko kokosowe",
            "mleczka kokosowego",
            "mleczko kokosowe",
            "mleczkiem kokosowym",
            "mleczka kokosowe",
            "mleczek kokosowych",
            "mleczkami kokosowymi"
        ]),

        ("gałka muszkatołowa",[
            "gałka muszkatołowa",
            "gałki muszkatołowej",
            "gałkę muszkatołową",
            "gałką muszkatołową",
            "gałki muszkatołowe",
            "gałek muszkatołowych",
            "gałkami muszkatołowymi"
        ]),

        ("czekolada mleczna",[
            "czekolada mleczna",
            "czekolady mlecznej",
            "czekoladę mleczną",
            "czekoladą mleczną",
            "czekolady mleczne",
            "czekolad mlecznych",
            "czekoladami mlecznymi"
        ]),

        ("masło czekoladowe z dodatkiem kakao",[
            "masło czekoladowe z dodatkiem kakao",
            "masła czekoladowego z dodatkiem kakao",
            "masło czekoladowe z dodatkiem kakao",
            "masłem czekoladowym z dodatkiem kakao",
            "masła czekoladowe z dodatkiem kakao",
            "maseł czekoladowych z dodatkiem kakao",
            "masłami czekoladowymi z dodatkiem kakao"
        ])
    ]
)
async def test_inflect_ingredient_names_with_adjectives(normalizer, word: str, expected: list[str]):
    result = await normalizer.inflect(word)

    assert result == expected



@pytest.mark.asyncio
@pytest.mark.parametrize(
    "word, expected",
    [
        ("czarny, suchy pieprz", [
            "czarny, suchy pieprz",
            "czarnego, suchego pieprzu",
            "czarny, suchy pieprz",
            "czarnym, suchym pieprzem",
            "czarne, suche pieprze",
            "czarnych, suchych pieprzy",
            "czarnymi, suchymi pieprzami"
        ]),
        ("naturalny, słodzony miód", [
            "naturalny, słodzony miód",
            "naturalnego, słodzonego miodu",
            "naturalny, słodzony miód",
            "naturalnym, słodzonym miodem",
            "naturalne, słodzone miody",
            "naturalnych, słodzonych miodów",
            "naturalnymi, słodzonymi miodami"
        ]),
            ("niebieskie żółtko jaja gotowane i obrane", [
            "niebieskie żółtko jaja gotowane i obrane",
            "niebieskiego żółtka jaja gotowanego i obranego",
            "niebieskie żółtko jaja gotowane i obrane",
            "niebieskim żółtkiem jaja gotowanym i obranym",
            "niebieskie żółtka jaj gotowane i obrane",
            "niebieskich żółtek jaj gotowanych i obranych",
            "niebieskimi żółtkami jaj gotowanymi i obranymi"
        ]),
        ("mąka kolorowa typu 2", [
            "mąka kolorowa typu 2",
            "mąki kolorowej typu 2",
            "mąkę kolorową typu 2",
            "mąką kolorową typu 2",
            "mąki kolorowe typu 2",
            "mąk kolorowych typu 2",
            "mąkami kolorowymi typu 2"
        ])
    ]
)
async def test_inflect_with_punctuation_marks(normalizer, word: str, expected: list[str]):
    result = await normalizer.inflect(word)

    assert result == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "word, expected",
    [
        ("niesłodzone kakao", [
            "niesłodzone kakao",
            "niesłodzonego kakao",
            "niesłodzone kakao",
            "niesłodzonym kakao",
            "niesłodzone kakao",
            "niesłodzonych kakao",
            "niesłodzonymi kakao"
        ]),
        ("niesłodzony cukier", [
            "niesłodzony cukier",
            "niesłodzonego cukru",
            "niesłodzony cukier",
            "niesłodzonym cukrem",
            "niesłodzone cukry",
            "niesłodzonych cukrów",
            "niesłodzonymi cukrami"
        ]),
        ("nieświeży śledź", [
            "nieświeży śledź",
            "nieświeżego śledzia",
            "nieświeżego śledzia",
            "nieświeżym śledziem",
            "nieświeże śledzie",
            "nieświeżych śledzi",
            "nieświeżymi śledziami"
        ]),
        ("nienaturalny jogurt", [
            "nienaturalny jogurt",
            "nienaturalnego jogurtu",
            "nienaturalny jogurt",
            "nienaturalnym jogurtem",
            "nienaturalne jogurty",
            "nienaturalnych jogurtów",
            "nienaturalnymi jogurtami"
        ])
    ]
)
async def test_inflect_with_negations(normalizer, word: str, expected: str):
    result = await normalizer.inflect(word)

    assert result == expected
