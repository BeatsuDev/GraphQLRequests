from __future__ import annotations

import dataclasses
import typing
from keyword import iskeyword
from typing import List, Optional

from typing_inspect import is_generic_type  # type: ignore

if typing.TYPE_CHECKING:  # pragma: no cover
    from .custom_type_hints import DataclassType
    from .query_method import QueryMethod


class Query:
    def __init__(
        self,
        dataclass_schema: DataclassType,
        fields: Optional[List[str | DataclassType | QueryMethod]] = None,
        indents: int = 4,
        start_indent: int = 0,
        strip_underscores_for_keywords: bool = True,
    ):
        self.dataclass_schema = dataclass_schema
        self.fields = fields
        self.indents = indents
        self.start_indent = start_indent
        self.strip = strip_underscores_for_keywords

    def _generate_fields(
        self,
        dataclass_schema: DataclassType,
        fields: Optional[List[str | DataclassType | QueryMethod]] = None,
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
            (name.strip("_") if iskeyword(name.strip("_")) else name): resolved_hints[
                name
            ]
            for name in field_names
            if name in included_fields
        }

        # Build the fields string
        formatted_fields = []

        # Helper functions that will be used to determine the type of the field
        def is_list(f):
            return is_generic_type(f) and f.__origin__ == list

        def is_primitive(f):
            return hasattr(f, "__name__") and f.__name__ in [
                "str",
                "int",
                "float",
                "bool",
            ]

        # First add the fields that are not QueryMethods (this will be added last)
        for field, field_type in resolved_field_types.items():

            # If the field is a dataclass, generate a new query for it
            if dataclasses.is_dataclass(field_type):
                field_string = (
                    field
                    + " "
                    + str(Query(field_type, indents=self.indents, start_indent=indents))
                )

            # If the field is a list containing a dataclass, generate a new query for the first dataclass in the list
            elif is_list(field_type) and dataclasses.is_dataclass(
                field_type.__args__[0]
            ):
                if dataclasses.is_dataclass(field_type.__args__[0]):
                    field_string = (
                        field
                        + " "
                        + str(
                            Query(
                                field_type.__args__[0],
                                indents=self.indents,
                                start_indent=indents,
                            )
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

        # Now add the fields that are QueryMethods (these were skipped in the
        # beginning because they don't have type hints or dataclass field)
        for query_method_field in included_fields:
            if (
                query_method_field.__class__.__name__ == "QueryMethod"
            ):  # Mypy doesn't recognize QueryMethod as a class
                formatted_fields.append(query_method_field._generate_query(self.indents + indents))  # type: ignore

        return "\n".join(formatted_fields)

    def _generate_query(self, indents: int = 4) -> str:
        query = (
            "{\n"
            + self._generate_fields(self.dataclass_schema, self.fields, indents)
            + "\n"
            + " " * (indents - self.indents)
            + "}"
        )
        return query

    def __str__(self) -> str:
        return self._generate_query(self.start_indent + self.indents)
