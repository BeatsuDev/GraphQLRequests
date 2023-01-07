from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Any, Dict, List

from .query import Query

if TYPE_CHECKING:
    from .utilities import DataclassType


class QueryMethod(Query):
    def __init__(
        self,
        method_name: str,
        dataclass_schema: DataclassType,
        args: Optional[Dict[str, Any]] = None,
        fields: Optional[List[str | Query | QueryMethod]] = None,
        indents: int = 4,
    ):
        super().__init__(dataclass_schema, fields, indents)
        self.method_name = method_name
        self.dataclass_schema = dataclass_schema
        self.args = args or {}

    def __str__(self) -> str:
        argument_list = []
        for key, value in self.args.items():
            if isinstance(value, str):
                argument_list.append(f'{key}: "{value}"')
            elif isinstance(value, bool):
                argument_list.append(f"{key}: {str(value).lower()}")
            else:
                argument_list.append(f"{key}: {value}")

        arguments = ", ".join(argument_list)
        return f"{self.method_name}({arguments}) " + super()._generate_query(self.indents)
