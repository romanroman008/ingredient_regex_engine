from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Optional, Union

PathLike = Union[str, Path]


def _resolve_dir(path: PathLike, base_dir: Optional[Path] = None) -> Path:
    p = Path(path).expanduser()

    if not p.is_absolute():
        if base_dir is not None:
            p = base_dir / p
        else:
            p = p.resolve()

    p = p.resolve()

    if p.exists() and not p.is_dir():
        raise ValueError(f"Expected directory, got file: {p}")

    p.mkdir(parents=True, exist_ok=True)
    return p


@dataclass(frozen=True, slots=True, kw_only=True)
class AgentConfig:
    model: str = "gpt-4o-mini"
    timeout: int = 20
    ensemble_size: int = 5
    max_retries: int = 3

@dataclass(frozen=True, slots=True, kw_only=True)
class FileStorageConfig:
    kind:Literal["file"] = "file"
    output_dir:PathLike

@dataclass(frozen=True, slots=True, kw_only=True)
class DatabaseStorageConfig:
    kind:Literal["database"] = "database"
    database_url:str
    echo:bool = False

StorageConfig = FileStorageConfig | DatabaseStorageConfig


@dataclass(frozen=True, slots=True, kw_only=True)
class EngineConfig:
    storage: StorageConfig
    parser: AgentConfig = field(default_factory=AgentConfig)
    categorizer: AgentConfig = field(default_factory=AgentConfig)




@dataclass(slots=True)
class EngineConfigDepr:
    output_dir: Path
    parser: "AgentConfig"
    categorizer: "AgentConfig"

    def __post_init__(self):
        self.output_dir = _resolve_dir(self.output_dir)

    @classmethod
    def create(
        cls,
        output_dir: PathLike,
        parser: "AgentConfig",
        categorizer: "AgentConfig",
        base_dir: Optional[PathLike] = None,
    ) -> "EngineConfig":
        base = Path(base_dir).resolve() if base_dir else None
        resolved_output = _resolve_dir(output_dir, base)

        return cls(
            output_dir=resolved_output,
            parser=parser,
            categorizer=categorizer,
        )
