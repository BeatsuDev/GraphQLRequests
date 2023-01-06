from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .query_method import QueryMethod
    from .utilities import DataclassType


class Query:
    def __init__(
        self,
        dataclass_schema: DataclassType,
        fields: list[str | Query | QueryMethod] | None = None,
        indent: int = 4,
    ):
        self.dataclass_schema = dataclass_schema
        self.fields = fields or []
        self.indent = indent

    def __str__(self) -> str:
        field_list = []
        for field in self.fields:
            if isinstance(field, str):
                field_list.append(field)
            elif isinstance(field, QueryMethod):
                field_list.append(str(field))
            elif isinstance(field, Query):
                field_list.append(str(field))
            else:
                raise TypeError(
                    f"Expected str, Query or QueryMethod, got {type(field)}"
                )

        fields = ", ".join(field_list)
        return f"{self.dataclass_schema} {{ {fields} }}"
