import logging
from typing import Optional, Sequence


from morfeusz2 import Morfeusz

from regex_engine.src.regex_engine.adapters.normalizers.dump.ingredient_name import split_phrase, join_tokens
from regex_engine.src.regex_engine.adapters.normalizers.morfeusz.morfeusz_utils import filter_non_cooking_related, \
    is_word_inflectionally_independent


from regex_engine.src.regex_engine.adapters.normalizers.morfeusz.morfeusz_utils import is_word_cooking_related, \
    tuples_to_word_analysis
from regex_engine.src.regex_engine.domain.models.grammar import SentencePart, GrammaticalCase, GrammaticalNumber, \
    GrammaticalGender
from regex_engine.src.regex_engine.application.dto import WordAnalysis, AnalysedPhrase, PositionedWord

logger = logging.getLogger("phrase_analyzer")

class PhraseAnalyser:
    def __init__(self, morfeusz:Morfeusz):
        self.morfeusz = morfeusz

        self._numbered_phrase:dict[int, str] = {}
        self._phrase_analysis: list[WordAnalysis] = []

        self._subject_index: int = -1
        self._subject:Optional[WordAnalysis] = None
        self._subject_variations:list[WordAnalysis] = []

        self._subject_related_adjectives: list[WordAnalysis] = []
        self._subject_related_adjectives_variations: list[WordAnalysis] = []

        self._dependent_noun: Optional[WordAnalysis] = None
        self._dependent_noun_variations: list[WordAnalysis] = []

        self._dependent_noun_related_adjectives: list[WordAnalysis] = []
        self._dependent_noun_related_adjectives_variations: list[WordAnalysis] = []




    def analyse(self, phrase:str) -> AnalysedPhrase:
        phrase_analysis = self.morfeusz.analyse(phrase)

        self._numbered_phrase = split_phrase(phrase)

        word_analysis = tuples_to_word_analysis(phrase_analysis)

        self._phrase_analysis = filter_non_cooking_related(word_analysis)

        subject_index = self._find_first_noun_index()
        self._subject_index= subject_index

        self._subject_variations = self._get_word_analysis_by_index(subject_index)

        self._dependent_noun_variations = self._get_dependent_noun_variations()

        if self._dependent_noun_variations:
            self._subject_related_adjectives_variations = self._get_related_adjectives(subject_index, -1)
            self._dependent_noun_related_adjectives_variations = self._get_related_adjectives(subject_index + 1, 1)

            subject = self._determine_correct_subject()
            self._subject = subject
            dependent_noun = self._determine_correct_dependent_noun()
            self._dependent_noun = dependent_noun

            if self._subject_related_adjectives_variations:
                self._subject_related_adjectives = self._determine_subject_related_adjectives()

            if self._dependent_noun_related_adjectives_variations:
                self._dependent_noun_related_adjectives = self._determine_dependent_noun_related_adjectives()

        else:
            self._subject_related_adjectives = self._get_related_adjectives(subject_index, -1) + self._get_related_adjectives(subject_index, 1)
            self._subject = self._determine_correct_subject()

        analysed_phrase =  self._create_analysed_phrase()
        self._clear()

        return analysed_phrase



    def _clear(self):
        self._numbered_phrase: dict[int, str] = {}
        self._phrase_analysis: list[WordAnalysis] = []

        self._subject_index: int = -1
        self._subject: Optional[WordAnalysis] = None
        self._subject_variations: list[WordAnalysis] = []

        self._subject_related_adjectives: list[WordAnalysis] = []
        self._subject_related_adjectives_variations: list[WordAnalysis] = []

        self._dependent_noun: Optional[WordAnalysis] = None
        self._dependent_noun_variations: list[WordAnalysis] = []

        self._dependent_noun_related_adjectives: list[WordAnalysis] = []
        self._dependent_noun_related_adjectives_variations: list[WordAnalysis] = []

    def _create_analysed_phrase(self):
        n_subject = PositionedWord(self._subject.position, self._subject)
        n_dependent_noun = None
        n_subject_adjectives = []
        n_dependent_noun_adjectives = []
        if self._dependent_noun:
            n_dependent_noun = PositionedWord(self._dependent_noun.position, self._dependent_noun)
            for adjective in self._dependent_noun_related_adjectives:
                n_dependent_noun_adjectives.append(PositionedWord(adjective.position, adjective))
        for subj_adj in self._subject_related_adjectives:
            n_subject_adjectives.append(PositionedWord(subj_adj.position, subj_adj))



        return AnalysedPhrase(subject=n_subject,
                              dependent_noun=n_dependent_noun,
                              subject_adjectives=n_subject_adjectives,
                              dependent_noun_adjectives=n_dependent_noun_adjectives,
                              phrase=self._numbered_phrase
                              )



    def _determine_correct_dependent_noun(self):
        result = []
        if not self._subject_variations:
            return None

        if len(self._dependent_noun_variations) == 1:
            return self._dependent_noun_variations[0]

        for variant in self._dependent_noun_variations:
            if variant.number & self._subject.number:
                result.append(variant)

        if not result:
            logger.warning("Could not determine proper dependent noun variation: %s", self._subject)
            logger.warning("Returning first one: %s", self._dependent_noun_variations[0])
            return self._dependent_noun_variations[0]

        if len(result) > 1:
            logger.warning("Found multiple dependent nouns: %s", result)
            logger.warning("Returning first one: %s", result[0])


        return result[0]


    def _determine_correct_subject(self) -> WordAnalysis:
        if len(self._subject_variations):
            return self._subject_variations[0]

        for variation in self._subject_variations:
            if is_word_inflectionally_independent(variation):
                return variation

        result = []

        for subject_variation in self._subject_variations:
            subj_genders = subject_variation.gender
            subj_cases = subject_variation.case
            subj_number = subject_variation.number

            for adjective_variation in self._related_adjectives_variations:
                if (subj_genders & adjective_variation.gender and
                        subj_cases & adjective_variation.case and
                        subj_number & adjective_variation.number):
                    result.append(subject_variation)

        if len(result) > 1:
            logger.warning("Found multiple subject variations: %s", result)
            logger.warning("Returning first one: %s", result[0])
            return result[0]

        if not result:
            logger.warning("Could not determine proper subject variation: %s", self._subject_variations)
            logger.warning("Returning first one: %s", self._subject_variations[0])

        return self._subject_variations[0]


    def _get_related_adjectives(self, index:int, direction:int):
        allowed_parts = {
            SentencePart.ADJECTIVE.value,
            SentencePart.PASSIVE_ADJECTIVAL_PARTICIPLE.value,
        }
        bridge_parts = {
            SentencePart.PUNCTUATION_MARK.value,
            SentencePart.CONJUNCTION.value,
        }
        result: list[WordAnalysis] = []

        if direction not in (-1, 1):
            raise ValueError("direction must be -1 or 1")

        if direction == 1:
            start = index + 1
            stop = len(self._numbered_phrase)
        else:
            start = index - 1
            stop = -1

        for index in range(start, stop, direction):
            variations = self._get_word_analysis_by_index(index)
            parts = {variation.part for variation in variations}

            result.extend(
                variation
                for variation in variations
                if variation.part in allowed_parts
            )

            if not (parts & allowed_parts or parts & bridge_parts):
                break

        return result




    def _get_subject_index(self) -> int:
        return self._subject_variations[0].position

    def _get_dependent_noun_variations(self) -> list[WordAnalysis]:
        right_neighbour_variations = self._get_word_analysis_by_index(self._subject_index + 1)
        return [word for word in right_neighbour_variations if word.part == SentencePart.NOUN.value]

    def _find_first_noun_index(self) -> int:
        sorted_analysis = sorted(self._phrase_analysis, key=lambda w: w.position)
        for word in sorted_analysis:
            if word.part == SentencePart.NOUN.value:
                return word.position
        raise ValueError("Could not determine subject in phrase: %s", join_tokens(self._numbered_phrase))

    def _get_word_analysis_by_index(self, index: int):
        return [word for word in self._phrase_analysis if word.position == index]