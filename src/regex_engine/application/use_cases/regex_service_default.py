import logging

from regex_engine.domain.enums import RegexKind, EnsureStatus
from regex_engine.domain.models.orchestrator import EnsureWordResult

from regex_engine.domain.models.regex_entry import RegexEntry

from regex_engine.domain.models.regex_registry import RegexRegistry

from regex_engine.ports.token_normalizer import TokenNormalizer

logger = logging.getLogger("regex_service")


class RegexServiceDefault:
    def __init__(self, kind: RegexKind, normalizer: TokenNormalizer):
        self._kind = kind
        self._normalizer = normalizer
        self._registry: RegexRegistry | None = None

    @property
    def kind(self):
        return self._kind

    @property
    def registry(self) -> RegexRegistry:
        if not self._registry:
            raise RuntimeError("Registry is not set for kind: %s" % self.kind)
        return self._registry

    @registry.setter
    def registry(self, registry: RegexRegistry) -> None:
        self._registry = registry




    async def ensure_word_included_in_registry(self, word: str) -> EnsureWordResult:
        try:
            if not self.registry:
                raise RuntimeError("Registry is not set for kind: %s" % self.kind)

            w = word.strip()
            if not w:
                logger.info("Word is empty")
                return self._build_ensure_word_result(EnsureStatus.SKIPPED_EMPTY, stem=w, word=w)

            hit = self._registry.match_best(w)
            if hit:
                logger.info("Word: %s can be matched by: %s", w, hit)
                return self._build_ensure_word_result(EnsureStatus.ALREADY_MATCHED, hit.stem, w)

            stem = await self._normalizer.stem(w)

            existing = self._registry.get(stem)

            if existing:
                logger.info("Found word %s stem: %s", w, existing)
                logger.info("Updating %s regex", stem)
                self._registry.add_variant(stem=stem, variant=w)
                logger.info("Done")
                return self._build_ensure_word_result(EnsureStatus.UPDATED_EXISTING, existing.stem, w)

            logger.info("Creating word variants...")
            word_variants = await self._normalizer.inflect(stem)
            logger.info("Done")

            entry = RegexEntry(stem, variants=word_variants)
            logger.info("Adding %s to database...", entry)
            self._registry.add_entry(entry)
            logger.info("Done")

            return self._build_ensure_word_result(EnsureStatus.CREATED_NEW, stem, w)
        except Exception as e:
            logger.error("Error encountered: %s", e)
            return self._build_ensure_word_result(EnsureStatus.FAILED, word, word, e)



    def _build_ensure_word_result(self, status: EnsureStatus, stem: str, word: str, exception = None) -> EnsureWordResult:
        return EnsureWordResult(kind=self.kind, status=status, stem=stem, word=word, exceptions=exception)


