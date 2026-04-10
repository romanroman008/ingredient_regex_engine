import logging

from regex_engine.domain.enums import RegexKind, EnsureStatus
from regex_engine.domain.models.orchestrator import EnsureWordResult

from regex_engine.domain.models.regex_entry import RegexEntry

from regex_engine.domain.models.regex_registry import RegexRegistry
from regex_engine.ports.regex_service import RegexService

from regex_engine.ports.token_normalizer import TokenNormalizer

logger = logging.getLogger("regex_service")



class RegexServiceDefault:
    def __init__(self,
                 normalizer: TokenNormalizer,
                 registry: RegexRegistry
                 ):
        self._normalizer = normalizer
        self._registry: RegexRegistry = registry



    async def ensure_word_included_in_registry(self, word: str) -> EnsureWordResult:
        kind = self._registry.kind
        try:
            w = word.strip()
            if not w:
                logger.info("Word is empty")
                return EnsureWordResult(kind=kind, status=EnsureStatus.SKIPPED_EMPTY, stem=w, word=w)

            hit = self._registry.match_best(w)
            if hit:
                logger.info("Word: %s can be matched by: %s", w, hit)
                return EnsureWordResult(kind=kind,status=EnsureStatus.ALREADY_MATCHED, stem=w, word=w)

            stem = await self._normalizer.stem(w)

            existing = self._registry.get(stem)

            if existing:
                logger.info("Found word %s stem: %s", w, existing)
                logger.info("Updating %s regex", stem)
                self._registry.add_variant(stem=stem, variant=w)
                logger.info("Done")
                return EnsureWordResult(kind=kind, status=EnsureStatus.UPDATED_EXISTING, stem=existing.stem, word=w)

            logger.info("Creating word variants...")
            word_variants = await self._normalizer.inflect(stem)
            logger.info("Done")

            entry = RegexEntry(stem, variants=word_variants)
            logger.info("Adding %s to database...", entry)
            self._registry.add_entry(entry)
            logger.info("Done")
            return EnsureWordResult(kind=kind, status=EnsureStatus.CREATED_NEW, stem=stem, word=w)

        except Exception as e:
            logger.error("Error encountered: %s", e)
            return EnsureWordResult(kind=kind, status=EnsureStatus.FAILED, stem=word, word=word, exception=e)






