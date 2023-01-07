from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .custom_type_hints import DataclassType


class Schema:
    def __init__(self, dataclass_schema: DataclassType):
        self.dataclass_schema = dataclass_schema

    def __str__(self) -> str:
        return "Not implemented yet"
