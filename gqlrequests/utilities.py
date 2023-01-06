from __future__ import annotations

from typing import Protocol


class DataclassType(Protocol):
    __dataclass_fields__: dict
