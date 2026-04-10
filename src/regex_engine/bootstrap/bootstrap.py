from regex_engine.adapters.categorizer.agent_categorizer import AgentCategorizer
from regex_engine.adapters.input_adapters.pandas_input_adapter import PandasInputAdapter
from regex_engine.adapters.input_adapters.string_input_adapter import StringInputAdapter
from regex_engine.adapters.input_adapters.string_iterable_input_adapter import StringIterableInputAdapter
from regex_engine.adapters.normalizers.morfeusz.adjective_normalizer import MorfeuszAdjectiveNormalizer
from regex_engine.adapters.normalizers.morfeusz.inflector.inflector import Inflector
from regex_engine.adapters.normalizers.morfeusz.ingredient_name import MorfeuszIngredientNameNormalizer
from regex_engine.adapters.normalizers.morfeusz.phrase_analyzer import PhraseAnalyser
from regex_engine.adapters.normalizers.morfeusz.unit_normalizer import MorfeuszUnitNormalizer
from regex_engine.adapters.parser.agent_ingredient_parser.agent_ingredient_parser import AgentIngredientParser
from regex_engine.application.use_cases.ingredient_filter_engine import IngredientFilterEngine
from regex_engine.application.use_cases.ingredient_regex_engine import IngredientRegexEngine
from regex_engine.application.use_cases.input_router import InputRouter
from regex_engine.application.use_cases.regex_orchestrator_default import RegexOrchestratorDefault
from regex_engine.application.use_cases.regex_resolver_default import RegexResolverDefault
from regex_engine.application.use_cases.regex_service_default import RegexServiceDefault
from regex_engine.domain.enums import RegexKind

import morfeusz2

from regex_engine.domain.models.registry_container import RegistryContainer
from regex_engine.ports.regex_registry import RegexRegistryRepository, IngredientRegexRegistryRepository


def load_regex_registries(regex_repository:RegexRegistryRepository,
                          categorized_ingredients_repository:IngredientRegexRegistryRepository) -> RegistryContainer:
    ingredient_registry = regex_repository.load(RegexKind.INGREDIENT_NAME)
    unit_registry = regex_repository.load(RegexKind.UNIT)
    unit_size_registry = regex_repository.load(RegexKind.UNIT_SIZE)
    condition_registry = regex_repository.load(RegexKind.INGREDIENT_CONDITION)
    or_conjunctions_registry = regex_repository.load(RegexKind.OR_CONJUNCTIONS)
    and_conjunctions_registry = regex_repository.load(RegexKind.AND_CONJUNCTIONS)

    categorized_ingredients_registry = categorized_ingredients_repository.load()

    return RegistryContainer(
        ingredient_registry=ingredient_registry,
        unit_registry=unit_registry,
        unit_size_registry=unit_size_registry,
        condition_registry=condition_registry,
        or_conjunctions_registry=or_conjunctions_registry,
        and_conjunctions_registry=and_conjunctions_registry,
    )


def build_engine(registries:RegistryContainer):
    morfeusz = morfeusz2.Morfeusz()

    inflector = Inflector(morfeusz)
    phrase_analyser = PhraseAnalyser(morfeusz)

    ingredient_normalizer = MorfeuszIngredientNameNormalizer(inflector=inflector,phrase_analyser=phrase_analyser)
    unit_normalizer = MorfeuszUnitNormalizer(inflector=inflector,morfeusz=morfeusz)
    unit_size_normalizer = MorfeuszAdjectiveNormalizer(inflector=inflector,morfeusz=morfeusz)
    ingredient_condition_normalizer = MorfeuszAdjectiveNormalizer(inflector=inflector,morfeusz=morfeusz)

    ingredient_service = RegexServiceDefault(RegexKind.INGREDIENT_NAME,
                                             ingredient_normalizer,
                                             registries.ingredient_registry)

    unit_service = RegexServiceDefault(RegexKind.UNIT,
                                       unit_normalizer,
                                       registries.unit_registry)

    unit_size_service = RegexServiceDefault(RegexKind.UNIT_SIZE,
                                            unit_size_normalizer,
                                            registries.unit_size_registry)

    ingredient_condition_service = RegexServiceDefault(RegexKind.INGREDIENT_CONDITION,
                                                       ingredient_condition_normalizer,
                                                       registries.condition_registry)

    regex_orchestrator = RegexOrchestratorDefault(
        ingredient_names=ingredient_service,
        ingredient_conditions=ingredient_condition_service,
        unit_sizes=unit_size_service,
        units=unit_service,
    )

    resolver = RegexResolverDefault(
        ingredient_names=registries.ingredient_registry,
        ingredient_conditions=registries.condition_registry,
        unit_sizes=registries.unit_size_registry,
        units=registries.unit_registry,
        or_conjunctions=registries.or_conjunctions_registry,
        and_conjunctions=registries.and_conjunctions_registry,
    )

    parser = AgentIngredientParser()

    filter_engine = IngredientFilterEngine(
        regex_orchestrator=regex_orchestrator,
        regex_resolver=resolver,
        parser=parser
    )

    categorizer = AgentCategorizer()

    input_adapters = [StringInputAdapter(), StringIterableInputAdapter(), PandasInputAdapter()]

    input_router_adapter = InputRouter(*input_adapters)

    return IngredientRegexEngine(filter_engine=filter_engine,
                                 categorizer=categorizer,
                                 input_adapter=input_router_adapter)








