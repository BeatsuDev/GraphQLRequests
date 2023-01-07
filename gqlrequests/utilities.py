from __future__ import annotations

from typing import Protocol


class DataclassType(Protocol):
    __name__: str
    __dataclass_fields__: dict