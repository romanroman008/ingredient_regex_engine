from dataclasses import dataclass
from typing import Any, Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class RecordMappingIssue:
    record_id: Any
    field: str
    raw_value: Any
    target_type: type[Any]
    reason: str

    def to_log_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "field": self.field,
            "raw_value": self.raw_value,
            "target_type": self.target_type.__name__,
            "reason": self.reason,
        }


@dataclass(frozen=True, slots=True)
class MappingResult(Generic[T]):
    items: list[T]
    issues: list[RecordMappingIssue]

    @property
    def has_issues(self) -> bool:
        return bool(self.issues)

