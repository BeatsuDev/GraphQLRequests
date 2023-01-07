from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from .query import Query

if TYPE_CHECKING:  # pragma: no cover
    from .custom_type_hints import DataclassType


class QueryMethod(Query):
    def __init__(
        self,
        method_name: str,
        dataclass_schema: DataclassType,
        args: Optional[Dict[str, Any]] = None,
        fields: Optional[List[str | DataclassType | QueryMethod]] = None,
        indents: int = 4,
        start_indent: int = 0,
    ):
        super().__init__(dataclass_schema, fields, indents, start_indent)
        self.method_name = method_name
        self.dataclass_schema = dataclass_schema
        self.args = args or {}

    def _create_method_head(self, indents: int = 0) -> str:
        argument_list = []
        for key, value in self.args.items():
            if isinstance(value, str):
                argument_list.append(f'{key}: "{value}"')
            elif isinstance(value, bool):
                argument_list.append(f"{key}: {str(value).lower()}")
            else:
                argument_list.append(f"{key}: {value}")
        return (
            " " * (self.start_indent + indents)
            + f"{self.method_name}({', '.join(argument_list)})"
        )

    def _generate_query(self, indents: int = 4) -> str:
        return f"{self._create_method_head(indents-4)} " + super()._generate_query(
            indents
        )

    def __str__(self) -> str:
        return self._generate_query(self.indents)
