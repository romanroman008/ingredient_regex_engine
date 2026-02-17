import pytest

from regex_engine.src.regex_engine.domain.models.regex_entry import RegexEntry



class TestRegexEntryInit:

    @pytest.mark.parametrize(
        "stem,variants,expected_variants",
        [
            ("mleko", ["mleko", "mleka"], {"mleko", "mleka"}),
            ("masło", ["masło", "masła", "masła"], {"masło", "masła"}),
            ("kakao", ["kakao"], {"kakao"}),
        ]

    )
    def test_happy_path(self, stem, variants, expected_variants):
        entry = RegexEntry(stem, variants)
        assert entry._stem == stem
        assert entry._variants == expected_variants


    @pytest.mark.parametrize(
        "stem,expected_variants",
        [
            ("mleko", {"mleko"}),
            ("masło", {"masło"}),
            ("kakao", {"kakao"}),
        ]
    )
    def test_empty_variants(self, stem, expected_variants):
        entry = RegexEntry(stem, {})
        assert entry._stem == stem
        assert entry._variants == expected_variants


    @pytest.mark.parametrize(
        "stem, variants",
        [
            ("", ["mleko"]),
            ("", [""]),
            ("    ", ["\n"]),
            ("\t", ["  "]),
        ]
    )
    def test_invalid_inputs(self, stem, variants):
        with pytest.raises(ValueError):
            RegexEntry(stem, variants)



class TestRegexEntryMatching:

    @pytest.mark.parametrize(
        "text",
        [
            "2 mleka w sklepie",
            "mleko",
            "masło i mleko",
            "Mleko",
            "2 Mleka i masła",
        ]
    )
    def test_contains_returns_true(self, text):
        entry = RegexEntry("mleko", ["mleko", "mleka"])
        assert entry.contains(text)

    @pytest.mark.parametrize(
        "text",
        [
            "2 mleczne batoniki w sklepie",
            "mlekowy",
            "masło i mlekoo",
            "mlek",
            "2mleka i masło",
            "mmlekoi",
        ]
    )
    def test_contains_returns_false(self, text):
        entry = RegexEntry("mleko", ["mleko", "mleka"])
        assert not entry.contains(text)


class TestRegexEntryFind:
    @pytest.mark.parametrize(
        "text, expected",
        [
            ("mleko", "mleko"),
            ("Mleko", "Mleko"),
            ("2 mleka i masło", "mleka"),
            ("Jedno mleko", "mleko"),
            ("", None),
            ("2 mleczne", None)

        ]
    )
    def test_find_happy_path(self, text, expected):
        entry = RegexEntry("mleko", ["mleko", "mleka"])
        assert entry.find(text) == expected




class TestRegexEntryFindSpan:
    @pytest.mark.parametrize(
        "text, expected",
        [
            ("mleko", (0,5)),
            ("2 mleka", (2, 7)),
            ("", None),
            ("43 masła", None),
        ]
    )
    def test_find_span_happy_path(self, text, expected):
        entry = RegexEntry("mleko", ["mleko", "mleka"])
        assert entry.find_span(text) == expected


class TestRegexEntryAddVariant:

    def test_add_variant_adds_new_value(self):
        entry = RegexEntry("mleko", ["mleko"])
        entry.add_variant("mleka")

        assert "mleka" in entry.variants
        assert entry.contains("mleka")

    def test_add_variant_strips_whitespace(self):
        entry = RegexEntry("mleko", ["mleko"])
        entry.add_variant("  mleka  ")

        assert "mleka" in entry.variants

    def test_add_variant_ignores_empty_string(self):
        entry = RegexEntry("mleko", ["mleko"])
        entry.add_variant("   ")

        assert entry.variants == {"mleko"}

    def test_add_variant_always_keeps_stem(self):
        entry = RegexEntry("mleko", [])
        entry.add_variant("mleka")

        assert "mleko" in entry.variants


class TestRegexEntryRemoveVariant:

    def test_remove_existing_variant(self):
        entry = RegexEntry("mleko", ["mleko", "mleka"])
        entry.remove_variant("mleka")

        assert "mleka" not in entry.variants
        assert not entry.contains("mleka")

    def test_remove_does_not_remove_stem(self):
        entry = RegexEntry("mleko", ["mleko", "mleka"])
        entry.remove_variant("mleko")

        assert "mleko" in entry.variants

    def test_remove_ignores_non_existing_variant(self):
        entry = RegexEntry("mleko", ["mleko"])
        entry.remove_variant("masło")

        assert entry.variants == {"mleko"}

    def test_remove_ignores_empty_string(self):
        entry = RegexEntry("mleko", ["mleko"])
        entry.remove_variant("   ")

        assert entry.variants == {"mleko"}



class TestRegexEntryEquality:

    def test_entries_with_same_stem_are_equal(self):
        e1 = RegexEntry("mleko", ["mleko"])
        e2 = RegexEntry("mleko", ["mleko", "mleka"])

        assert e1 == e2
        assert hash(e1) == hash(e2)

    def test_entries_with_different_stem_are_not_equal(self):
        e1 = RegexEntry("mleko", ["mleko"])
        e2 = RegexEntry("maslo", ["maslo"])

        assert e1 != e2

    def test_entry_can_be_used_in_set(self):
        e1 = RegexEntry("mleko", ["mleko"])
        e2 = RegexEntry("mleko", ["mleka"])

        s = {e1, e2}
        assert len(s) == 1
