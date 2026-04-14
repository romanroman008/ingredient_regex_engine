# tests/test_word_models.py

from dataclasses import FrozenInstanceError
import pytest

from regex_engine.domain.models.grammar import SentencePart, GradationDegree

from regex_engine.application.dto.word_analysis import WordAnalysis, GeneratedWord


class TestWordAnalysisBuild:
    def test_build_sets_empty_defaults_when_none_passed(self):
        result = WordAnalysis._build(
            position=0,
            lemma="kot",
            surface="kot",
            part=SentencePart.NOUN,
        )

        assert result.position == 0
        assert result.lemma == "kot"
        assert result.surface == "kot"
        assert result.part is SentencePart.NOUN
        assert result.number == set()
        assert result.case == set()
        assert result.gender == set()
        assert result.degree is None
        assert result.annotations == []

    def test_build_preserves_passed_values(self):
        result = WordAnalysis._build(
            position=3,
            lemma="kolorowy",
            surface="kolorowy",
            part=SentencePart.ADJECTIVE,
            number={"sg"},
            case={"nom"},
            gender={"m1"},
            degree=GradationDegree.POSITIVE,
            annotations=["attr"],
        )

        assert result.position == 3
        assert result.lemma == "kolorowy"
        assert result.surface == "kolorowy"
        assert result.part is SentencePart.ADJECTIVE
        assert result.number == {"sg"}
        assert result.case == {"nom"}
        assert result.gender == {"m1"}
        assert result.degree is GradationDegree.POSITIVE
        assert result.annotations == ["attr"]

    def test_build_creates_independent_defaults(self):
        a = WordAnalysis._build(
            position=0,
            lemma="kot",
            surface="kot",
            part=SentencePart.NOUN,
        )
        b = WordAnalysis._build(
            position=1,
            lemma="pies",
            surface="pies",
            part=SentencePart.NOUN,
        )

        assert a.number is not b.number
        assert a.case is not b.case
        assert a.gender is not b.gender
        assert a.annotations is not b.annotations

    def test_instance_is_frozen(self):
        obj = WordAnalysis._build(
            position=0,
            lemma="kot",
            surface="kot",
            part=SentencePart.NOUN,
        )

        with pytest.raises(FrozenInstanceError):
            obj.lemma = "pies"

    def test_instance_uses_slots(self):
        obj = WordAnalysis._build(
            position=0,
            lemma="kot",
            surface="kot",
            part=SentencePart.NOUN,
        )

        with pytest.raises(
            (AttributeError, TypeError)
        ):  # zależnie od implementacji/class layout
            obj.some_random_attr = 123


class TestWordAnalysisFromTuple:
    def test_from_tuple_parses_noun(self):
        analysis = (
            0,
            1,
            ("kot", "kot", "subst:sg:nom:m1", [], ["nazwa_pospolita"]),
        )

        result = WordAnalysis.from_tuple(analysis)

        assert result.position == 0
        assert result.surface == "kot"
        assert result.lemma == "kot"
        assert result.part is SentencePart.NOUN
        assert result.number == {"sg"}
        assert result.case == {"nom"}
        assert result.gender == {"m1"}
        assert result.degree is None
        assert result.annotations == ["nazwa_pospolita"]

    def test_from_tuple_parses_adjective(self):
        analysis = (
            0,
            1,
            ("kolorowy", "kolorowy", "adj:sg:nom:m1:pos", [], ["attr"]),
        )

        result = WordAnalysis.from_tuple(analysis)

        assert result.position == 0
        assert result.surface == "kolorowy"
        assert result.lemma == "kolorowy"
        assert result.part is SentencePart.ADJECTIVE
        assert result.number == {"sg"}
        assert result.case == {"nom"}
        assert result.gender == {"m1"}
        assert result.degree is GradationDegree.POSITIVE
        assert result.annotations == ["attr"]

    def test_from_tuple_parses_preposition_without_inflection_fields(self):
        analysis = (
            5,
            6,
            ("o", "o", "prep:loc", [], []),
        )

        result = WordAnalysis.from_tuple(analysis)

        assert result.position == 5
        assert result.surface == "o"
        assert result.lemma == "o"
        assert result.part is SentencePart.PREPOSITION
        assert result.number == set()
        assert result.case == set()
        assert result.gender == set()
        assert result.degree is None
        assert result.annotations == []

    def test_from_tuple_maps_unknown_part_to_unknown(self):
        analysis = (
            0,
            1,
            ("xyz", "xyz", "doesnotexist:foo:bar", [], []),
        )

        result = WordAnalysis.from_tuple(analysis)

        assert result.part is SentencePart.UNKNOWN
        assert result.number == set()
        assert result.case == set()
        assert result.gender == set()
        assert result.degree is None

    def test_from_tuple_raises_value_error_for_invalid_degree(self):
        analysis = (
            0,
            1,
            ("kolorowy", "kolorowy", "adj:sg:nom:m1:not-a-degree", [], []),
        )

        with pytest.raises(ValueError):
            WordAnalysis.from_tuple(analysis)

    def test_from_tuple_raises_value_error_for_invalid_outer_tuple_shape(self):
        analysis = (
            0,
            1,
        )

        with pytest.raises(ValueError):
            WordAnalysis.from_tuple(analysis)

    def test_from_tuple_raises_value_error_for_invalid_inner_tuple_shape(self):
        analysis = (
            0,
            1,
            ("kot", "kot"),
        )

        with pytest.raises(ValueError):
            WordAnalysis.from_tuple(analysis)

    def test_from_tuple_raises_attribute_error_when_morph_tag_is_none(self):
        analysis = (
            0,
            1,
            ("kot", "kot", None, [], []),
        )

        with pytest.raises(AttributeError):
            WordAnalysis.from_tuple(analysis)

    def test_from_tuple_raises_type_error_when_analysis_is_none(self):
        with pytest.raises(TypeError):
            WordAnalysis.from_tuple(None)


class TestGeneratedWordBuild:
    def test_build_sets_empty_defaults_when_none_passed(self):
        result = GeneratedWord._build(
            lemma="kot",
            surface="kot",
            part=SentencePart.NOUN,
        )

        assert result.lemma == "kot"
        assert result.surface == "kot"
        assert result.part is SentencePart.NOUN
        assert result.number == set()
        assert result.case == set()
        assert result.gender == set()
        assert result.degree is None
        assert result.annotations == []

    def test_build_preserves_passed_values(self):
        result = GeneratedWord._build(
            lemma="kolorowy",
            surface="kolorowy",
            part=SentencePart.ADJECTIVE,
            number={"sg"},
            case={"nom"},
            gender={"m1"},
            degree=GradationDegree.POSITIVE,
            annotations=["attr"],
        )

        assert result.lemma == "kolorowy"
        assert result.surface == "kolorowy"
        assert result.part is SentencePart.ADJECTIVE
        assert result.number == {"sg"}
        assert result.case == {"nom"}
        assert result.gender == {"m1"}
        assert result.degree is GradationDegree.POSITIVE
        assert result.annotations == ["attr"]

    def test_build_creates_independent_defaults(self):
        a = GeneratedWord._build(
            lemma="kot",
            surface="kot",
            part=SentencePart.NOUN,
        )
        b = GeneratedWord._build(
            lemma="pies",
            surface="pies",
            part=SentencePart.NOUN,
        )

        assert a.number is not b.number
        assert a.case is not b.case
        assert a.gender is not b.gender
        assert a.annotations is not b.annotations

    def test_instance_is_frozen(self):
        obj = GeneratedWord._build(
            lemma="kot",
            surface="kot",
            part=SentencePart.NOUN,
        )

        with pytest.raises(FrozenInstanceError):
            obj.lemma = "pies"

    def test_instance_uses_slots(self):
        obj = GeneratedWord._build(
            lemma="kot",
            surface="kot",
            part=SentencePart.NOUN,
        )

        with pytest.raises((AttributeError, TypeError)):
            obj.some_random_attr = 123


class TestGeneratedWordFromTuple:
    def test_from_tuple_parses_noun(self):
        analysis = ("kot", "kot", "subst:sg:nom:m1", [], ["nazwa_pospolita"])

        result = GeneratedWord.from_tuple(analysis)

        assert result.surface == "kot"
        assert result.lemma == "kot"
        assert result.part is SentencePart.NOUN
        assert result.number == {"sg"}
        assert result.case == {"nom"}
        assert result.gender == {"m1"}
        assert result.degree is None

    def test_from_tuple_parses_preposition_without_inflection_fields(self):
        analysis = ("o", "o", "prep:loc", [], [])

        result = GeneratedWord.from_tuple(analysis)

        assert result.surface == "o"
        assert result.lemma == "o"
        assert result.part is SentencePart.PREPOSITION
        assert result.number == set()
        assert result.case == set()
        assert result.gender == set()
        assert result.degree is None

    def test_from_tuple_raises_value_error_for_invalid_degree(self):
        analysis = ("kolorowy", "kolorowy", "adj:sg:nom:m1:not-a-degree", [], [])

        with pytest.raises(ValueError):
            GeneratedWord.from_tuple(analysis)

    def test_from_tuple_raises_value_error_for_invalid_tuple_shape(self):
        analysis = ("kot", "kot")

        with pytest.raises(ValueError):
            GeneratedWord.from_tuple(analysis)

    def test_from_tuple_raises_attribute_error_when_morph_tag_is_none(self):
        analysis = ("kot", "kot", None, [], [])

        with pytest.raises(AttributeError):
            GeneratedWord.from_tuple(analysis)

    def test_from_tuple_raises_type_error_when_analysis_is_none(self):
        with pytest.raises(TypeError):
            GeneratedWord.from_tuple(None)


class TestHelpers:
    def test_to_part_returns_unknown_for_invalid_value(self):
        result = WordAnalysis._to_part("definitely-not-a-real-part")
        assert result is SentencePart.UNKNOWN

    def test_split_tag_returns_empty_list_for_missing_index(self):
        result = WordAnalysis._split_tag("subst:sg:nom:m1", 99)
        assert result == []

    def test_split_tag_returns_split_values_for_existing_index(self):
        result = WordAnalysis._split_tag("adj:pl:nom.voc:m1.m2:pos", 2)
        assert result == ["nom", "voc"]