from unittest.mock import AsyncMock, create_autospec

import pytest

from regex_engine.src.regex_engine.application.use_cases.regex_service_default import RegexServiceDefault
from regex_engine.src.regex_engine.domain.enums import RegexKind, EnsureStatus
from regex_engine.src.regex_engine.domain.models.regex_entry import RegexEntry
from regex_engine.src.regex_engine.domain.models.regex_registry import RegexRegistry
from regex_engine.src.regex_engine.ports.token_normalizer import TokenNormalizer


@pytest.fixture()
def regex_kind() -> RegexKind:
    return next(iter(RegexKind))


@pytest.fixture()
def regex_entry() -> RegexEntry:
    return create_autospec(RegexEntry, instance=True, spec_set=True)


@pytest.fixture()
def normalizer() -> TokenNormalizer:
    normalizer = create_autospec(TokenNormalizer, instance=True, spec_set=True)
    normalizer.stem = AsyncMock()
    normalizer.inflect = AsyncMock()
    return normalizer


@pytest.fixture()
def registry() -> RegexRegistry:
    r = create_autospec(RegexRegistry, instance=True, spec_set=True)

    # bezpieczne defaulty (najczęstszy flow)
    r.match_best.return_value = None
    r.get.return_value = None
    r.get_all.return_value = tuple()

    # metody mutujące: default = brak efektu
    r.add_entry.return_value = None
    r.remove_entry.return_value = None
    r.add_variant.return_value = None
    r.remove_variant.return_value = None

    # swap_match: sensowny default (brak dopasowania)
    r.swap_match.side_effect = lambda text, replacement: text

    return r


@pytest.fixture()
def service(regex_kind: RegexKind, normalizer: TokenNormalizer, registry: RegexRegistry) -> RegexServiceDefault:
    svc = RegexServiceDefault(regex_kind, normalizer)
    svc.registry = registry
    return svc


@pytest.mark.asyncio
async def test_ensure_word_included_in_registry__registry_not_set__raises(regex_kind, normalizer):
    svc = RegexServiceDefault(regex_kind, normalizer)

    with pytest.raises(RuntimeError):
        await svc.ensure_word_included_in_registry("gibberish")


@pytest.mark.asyncio
@pytest.mark.parametrize("word", ["", "  ", "\n", "\n\t "])
async def test_ensure_word_included_in_registry__word_empty__skips(service: RegexServiceDefault, word: str):
    result = await service.ensure_word_included_in_registry(word)

    assert result.kind == service.kind
    assert result.status == EnsureStatus.SKIPPED_EMPTY
    assert result.stem == ""
    assert result.word == ""


@pytest.mark.asyncio
@pytest.mark.parametrize("word", ["", "  ", "\n", "\n\t "])
async def test_ensure_word_included_in_registry__word_empty__does_not_call_dependencies(
    service: RegexServiceDefault, word: str
):
    await service.ensure_word_included_in_registry(word)

    # registry metody nie powinny być wołane
    service.registry.match_best.assert_not_called()
    service.registry.get.assert_not_called()
    service.registry.add_variant.assert_not_called()
    service.registry.add_entry.assert_not_called()

    # normalizer też nie
    service._normalizer.stem.assert_not_called()
    service._normalizer.inflect.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "word, hit_stem, expected_word",
    [
        ("masło", "masło", "masło"),
        ("  vanilia", "vanilia", "vanilia"),
        ("sok  pomarańczowy", "HIT_STEM", "sok  pomarańczowy"),  # word nie traci spacji wewnątrz
        ("  masło  \n ", "masło", "masło"),
    ],
)
async def test_ensure_word_in_registry__word_can_be_matched__returns_matched(
    service: RegexServiceDefault,
    regex_entry: RegexEntry,
    word: str,
    hit_stem: str,
    expected_word: str,
):
    # Arrange
    regex_entry.stem = hit_stem
    service.registry.match_best.return_value = regex_entry

    # Act
    result = await service.ensure_word_included_in_registry(word)

    # Assert - rezultat
    assert result.kind == service.kind
    assert result.status == EnsureStatus.ALREADY_MATCHED
    assert result.stem == hit_stem
    assert result.word == expected_word

    # Assert - orkiestracja
    service.registry.match_best.assert_called_once_with(expected_word)
    service._normalizer.stem.assert_not_called()
    service._normalizer.inflect.assert_not_called()
    service.registry.get.assert_not_called()
    service.registry.add_variant.assert_not_called()
    service.registry.add_entry.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "word, expected_stem, expected_word",
    [
        ("mleka", "mleko", "mleka"),
        ("ciasta czekoladowego", "ciasto_czekoladowe", "ciasta czekoladowego"),
        ("\n maślanki  ", "maślanka", "maślanki"),
    ],
)
async def test_ensure_word_in_registry__word_does_not_match_stem_exists__updates_existing(
    service: RegexServiceDefault,
    regex_entry: RegexEntry,
    word: str,
    expected_stem: str,
    expected_word: str,
):
    # Arrange
    regex_entry.stem = expected_stem
    service.registry.match_best.return_value = None
    service._normalizer.stem.return_value = expected_stem
    service.registry.get.return_value = regex_entry

    # Act
    result = await service.ensure_word_included_in_registry(word)

    # Assert - rezultat
    assert result.kind == service.kind
    assert result.status == EnsureStatus.UPDATED_EXISTING
    assert result.stem == expected_stem
    assert result.word == expected_word

    # Assert - orkiestracja (kolejność mniej istotna, ale call’e i argumenty tak)
    service.registry.match_best.assert_called_once_with(expected_word)
    service._normalizer.stem.assert_awaited_once_with(expected_word)
    service.registry.get.assert_called_once_with(expected_stem)
    service.registry.add_variant.assert_called_once_with(stem=expected_stem, variant=expected_word)

    service._normalizer.inflect.assert_not_called()
    service.registry.add_entry.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "word, expected_stem, expected_word, variants",
    [
        ("masło", "masło", "masło", ("masło", "masła")),
        ("mleko", "mleko", "mleko", ("mleko", "mleka")),
    ],
)
async def test_ensure_word_in_registry__word_does_not_match_stem_not_exists__creates_new(
    service: RegexServiceDefault,
    word: str,
    expected_stem: str,
    expected_word: str,
    variants: tuple[str, ...],
):
    # Arrange
    service.registry.match_best.return_value = None
    service.registry.get.return_value = None
    service._normalizer.stem.return_value = expected_stem
    service._normalizer.inflect.return_value = variants

    # Act
    result = await service.ensure_word_included_in_registry(word)

    # Assert - rezultat
    assert result.kind == service.kind
    assert result.status == EnsureStatus.CREATED_NEW
    assert result.stem == expected_stem
    assert result.word == expected_word

    # Assert - orkiestracja
    service.registry.match_best.assert_called_once_with(expected_word)
    service._normalizer.stem.assert_awaited_once_with(expected_word)
    service.registry.get.assert_called_once_with(expected_stem)
    service._normalizer.inflect.assert_awaited_once_with(expected_stem)
    service.registry.add_entry.assert_called_once()

    # Assert - poprawność dodawanego entry (bez zależności od __eq__)
    added_entry = service.registry.add_entry.call_args.args[0]
    assert isinstance(added_entry, RegexEntry)
    assert added_entry.stem == expected_stem
    assert tuple(added_entry.variants) == variants

    # Dodatkowo: nie powinno aktualizować wariantu istniejącego
    service.registry.add_variant.assert_not_called()
