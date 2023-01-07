from __future__ import annotations

import dataclasses
import typing
from types import GenericAlias

if typing.TYPE_CHECKING:
    from gqlrequests.query_method import QueryMethod
    from .utilities import DataclassType


class Query:
    def __init__(
        self,
        dataclass_schema: DataclassType,
        fields: list[str | Query | QueryMethod] | None = None,
        indents: int = 4,
    ):
        self.dataclass_schema = dataclass_schema
        self.fields = fields
        self.indents = indents

    def _generate_fields(
        self,
        dataclass_schema: DataclassType,
        fields: list[str | Query | QueryMethod] | None,
        indents: int = 0,
    ) -> str:
        """A recursive method to generate the fields of a query."""
        # Get all the datafields of the dataclass (This is a bit of a workaround
        # because from __future__ import annotations turns the type hints into
        # strings, so we need to resolve them manually)
        # See: https://stackoverflow.com/a/51953411/8594404
        resolved_hints = typing.get_type_hints(dataclass_schema)
        field_names = [field.name for field in dataclasses.fields(dataclass_schema)]

        # Only include the fields of the dataclass that are in the fields list
        included_fields = fields or field_names
        resolved_field_types = {
            name: resolved_hints[name]
            for name in field_names
            if name in included_fields
        }

        # Build the fields string
        formatted_fields = []
        for field, field_type in resolved_field_types.items():
            is_list = (
                lambda f: isinstance(f, GenericAlias) and f.__origin__ == list
            )  # noqa: E731
            is_primitive = lambda f: f.__name__ in [
                "str",
                "int",
                "float",
                "bool",
            ]  # noqa: E731

            # If the field is a dataclass, generate a new query for it
            if dataclasses.is_dataclass(field_type):
                field_string = Query(field_type)._generate_query(indents + self.indents)

            # If the field is a list containing a dataclass, generate a new query for the first dataclass in the list
            elif is_list(field_type) and dataclasses.is_dataclass(
                field_type.__args__[0]
            ):
                if dataclasses.is_dataclass(field_type.__args__[0]):
                    field_string = (
                        field
                        + " "
                        + Query(field_type.__args__[0])._generate_query(
                            indents + self.indents
                        )
                    )

            # If the field is a list of primtives, or just a primtive, only add the field name
            elif is_primitive(field_type) or (
                is_list(field_type) and is_primitive(field_type.__args__[0])
            ):
                field_string = field

            # If the field is not a primitive type or a dataclass (or any of those two in a list), raise an error
            else:
                raise ValueError(
                    f'The field "{field}" of "{self.dataclass_schema.__name__}" is not'
                    "a primitive type or a dataclass, or a list containing either."
                )

            formatted_fields.append(" " * indents + field_string)

        # Remove the last newline (this gets added in _generate_query)
        return "\n".join(formatted_fields)

    def _generate_query(self, indents: int = 4) -> str:
        query = (
            "{\n"
            + self._generate_fields(self.dataclass_schema, self.fields, indents)
            + "\n"
            + " " * (indents - 4)
            + "}"
        )
        return query

    def __str__(self) -> str:
        return self._generate_query(self.indents)
