"""Contains abstract classes to be inherited by classes with types hints.
These are then use to build GraphQL query strings in a Pythonic way."""

from __future__ import annotations

import abc
import enum
import typing


class QueryBuilder(abc.ABC):
    """An abstract class used to build GraphQL queries.

    This class should be inherited by a class with type hints and only
    supports single-leveled inheritance. This version of the QueryBuilder
    does not support reserved keywords as field names. To use reserved
    keywords, check the `StrippedUnderscoresQueryBuilder` class.

    Example usage:

        class EveryType(gqlrequests.QueryBuilder):
            id: int
            age: int
            money: float
            name: str
            company: bool

        every_type = EveryType()
        every_type.id = str

        graphql_query_string = every_type.build()

    """

    SUPPORTED_TYPES = (int, float, str, bool)

    _resolved_fields: dict[str, type | QueryBuilder] | None = None

    indent_size: int = 4
    start_indents: int = 0
    fields: list[str] | None = None
    func_name: str | None = None

    def __init__(self, **options):
        self._resolved_fields = typing.get_type_hints(self)
        self._process_options(options)

    def _process_options(self, options: dict) -> None:
        """Applies the given options to the builder state. This action
        overrides the current values of the builder."""
        if passed_fields := options.pop("fields", None):
            if not isinstance(passed_fields, list):
                raise ValueError("The fields option must be a list of strings.")
            if not all(isinstance(field, str) for field in passed_fields):
                raise ValueError("The fields option must be a list of strings.")

            for field in passed_fields:
                if field not in (self._resolved_fields or []):
                    raise AttributeError(
                        f"{field} is not a valid field for this builder."
                    )

        self.fields = passed_fields
        self.indent_size = options.pop("indent_size", self.indent_size)
        self.start_indents = options.pop("start_indents", self.start_indents)
        self.func_name = options.pop("func_name", self.func_name)

        if options:
            raise ValueError(
                "The following options are not valid options for a"
                "QueryBuilder: " + ", ".join(options.keys())
            )

    def build(self) -> str:
        """Generates a GraphQL query string based on the fields set in the
        builder."""
        if self.fields == []:
            raise ValueError("No fields were selected for the query builder.")
        build_output = "{\n"
        build_output += self._generate_fields()
        build_output += " " * self.start_indents + "}\n"
        return build_output

    def _generate_fields(self) -> str:
        # Guards
        fields_to_generate: dict[str, type | QueryBuilder] = {}

        if not self._resolved_fields:
            raise ValueError("No fields were set for this builder.")

        if self.fields:
            for field in self.fields:
                if field not in self._resolved_fields:
                    raise AttributeError(
                        f"{field} is not a valid field for this builder."
                    )
                fields_to_generate[field] = self._resolved_fields[field]
        else:
            fields_to_generate = self._resolved_fields.copy()

        # Actual generation
        fields_string_output = ""
        whitespaces = " " * self.start_indents + " " * self.indent_size

        for field, field_type in fields_to_generate.items():
            # {
            #    name: str
            #    NestedType  # <---
            # }
            if type(field_type) in (type, abc.ABCMeta) and issubclass(
                field_type, QueryBuilder
            ):  # type: ignore
                FieldBuilder = field_type
                field_builder = FieldBuilder(  # type: ignore
                    start_indents=len(whitespaces), indent_size=self.indent_size
                )
                fields_string_output += whitespaces + f"{field} {field_builder.build()}"

            # query = EveryType()
            # query.something = NestedType(fields=["name"]) # <---
            elif type(field_type) != type and isinstance(field_type, QueryBuilder):
                field_builder = field_type
                field_builder.start_indents = len(whitespaces)
                fields_string_output += whitespaces + f"{field} {field_builder.build()}"

            # {
            #   name
            # }
            elif self._resolved_fields[field] in self.SUPPORTED_TYPES or (
                type(field_type) == enum.EnumType
            ):
                fields_string_output += whitespaces + field + "\n"

            else:
                raise ValueError(f"Could not build {field} of type {field_type}.")

        return fields_string_output
