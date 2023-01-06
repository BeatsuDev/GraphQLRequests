from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .query import Query

if TYPE_CHECKING:
    from .utilities import DataclassType


class QueryMethod(Query):
    def __init__(
        self,
        method_name: str,
        dataclass_schema: DataclassType,
        method_args: dict[str, Any],
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.method_name = method_name
        self.method_args = method_args

    def __str__(self) -> str:
        argument_list = []
        for key, value in self.method_args.items():
            if isinstance(value, str):
                argument_list.append(f'{key}: "{value}"')
            else:
                argument_list.append(f"{key}: {value}")

        arguments = ", ".join(argument_list)
        return f"{self.method_name}({arguments}) " + str(self.dataclass_schema)
