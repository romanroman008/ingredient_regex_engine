import re
from regex_engine.src.regex_engine.domain.enums import RegexKind

ENUM_TOKEN_RE = re.compile(
    "|".join(
        re.escape(k.name)
        for k in sorted(RegexKind, key=lambda x: len(x.name), reverse=True)
    )
)

TRASH_RE = re.compile(
    r"[,\.;:()\[\]{}\"'“”‘’\-–—/\\*+=|~^]"
)

AND_CONJ_RE = re.compile(r"\b(?:i|oraz)\b", flags=re.IGNORECASE)

OR_CONJ_RE = re.compile(
    r"\b(?:albo|lub|bądź)\b",
    flags=re.IGNORECASE | re.UNICODE
)

AND_CONJ_BETWEEN_NUMBERS_RE = re.compile(
    r"(?<=\d)\s+(?:i|oraz)\s+(?=\d+(?:[.,]\d+)?(?:/\d+)?)",
    flags=re.IGNORECASE
)