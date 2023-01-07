from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .utilities import DataclassType


class Schema:
    def __init__(self, dataclass_schema: DataclassType):
        self.dataclass_schema = dataclass_schema

    def __str__(self) -> str:
        return "Not implemented yet"
