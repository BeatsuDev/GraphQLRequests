"""Contains abstract classes to be inherited by classes with types hints.
These are then use to build GraphQL query strings in a Pythonic way."""

from __future__ import annotations

import abc
import enum
import inspect
import typing
from typing import Any, Dict


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

    # Resolved fields are the fields set in the class with type hints
    # and remains unchanged. It is used to validate the fields property
    _resolved_fields: Dict[str, type | QueryBuilder] | None = None
    _build_function: bool = False

    indent_size: int = 4
    start_indents: int = 0
    build_fields: Dict[str, Any] | None = None
    func_name: str | None = None
    func_args: Dict[str, Any] | None = None

    def __init__(self, **options):
        self._resolved_fields = typing.get_type_hints(self)
        if not self._resolved_fields:
            raise ValueError("A QueryBuilder must have type hints to build a query.")

        self._process_options(options)

    def _process_options(self, options: Dict[str, Any]) -> None:
        """Applies the given options to the builder state. This action
        overrides the current values of the builder."""
        if not self._resolved_fields:
            raise ValueError("Cannot process options without any resolved fields.")

        if passed_fields := options.pop("fields", list(self._resolved_fields.keys())):
            if not isinstance(passed_fields, list):
                raise ValueError("The fields option must be a list of strings.")
            if not all(isinstance(field, str) for field in passed_fields):
                raise ValueError("The fields option must be a list of strings.")

            for field in passed_fields:
                if self._resolved_fields is None or field not in self._resolved_fields:
                    raise AttributeError(
                        f"{field} is not a valid field for this builder."
                    )

        self.build_fields = { key: self._resolved_fields[key] for key in passed_fields }
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
        if self.build_fields is None:
            raise ValueError("No fields were selected for the query builder. Cannot build an empty query.")

        if self._build_function:
            return self._generate_function()

        if len(self.build_fields.keys()) == 0:
            raise ValueError("No fields were selected for the query builder.")
        build_output = "{\n"
        build_output += self._generate_fields()
        build_output += " " * self.start_indents + "}\n"
        return build_output

    def _generate_fields(self) -> str:
        # Guards
        fields_to_generate: Dict[str, type | QueryBuilder] = {}

        if not self._resolved_fields:
            raise ValueError("No fields were set for this builder.")
        
        if not self.build_fields:
            fields_to_generate = self._resolved_fields.copy()
        else:
            fields_to_generate = self.build_fields.copy()

        # TODO: This might not be necessary... Or at least could be optimized
        # Double check if the fields are valid        
        for name, value in fields_to_generate.items():
            if not self._valid_field(name, value):
                raise ValueError(f"{name} is not a valid field for this builder.")

        # Actual generation
        fields_string_output = ""
        whitespaces = " " * self.start_indents + " " * self.indent_size

        for field, field_type in fields_to_generate.items():
            # {
            #    name: str
            #    NestedType  # <---
            # }
            if type(field_type) in (type, abc.ABCMeta) and issubclass(
                field_type, QueryBuilder # type: ignore
            ):
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
                type(field_type) == enum.EnumMeta
            ):
                fields_string_output += whitespaces + field + "\n"

            else:
                raise ValueError(f"Could not build {field} of type {field_type}.")

        return fields_string_output
    
    def __call__(self, **args) -> QueryBuilder:
        """After calling this method, the builder will build a function."""
        if not self.func_name:
            raise ValueError("No function name was set for this builder.")

        # TODO: Add support for non-primitive arguments
        for key, value in args.items():
            if type(value) not in self.SUPPORTED_TYPES:
                raise ValueError(
                    f"Function argument {key} of {self.func_name} must be of" +
                    f"the following types: {self.SUPPORTED_TYPES}"
                )

        self.func_args = args
        self._build_function = True

        return self

    def _generate_function(self) -> str:
        func_args = ""
        if self.func_args:
            func_args = ", ".join(
                f"{key}: {value}" for key, value in self.func_args.items()
            )

        # Reset temporarily so that the next build call builds the rest of the query
        self._build_function = False
        build_output = f"{self.func_name}({func_args}) {self.build()}"
        self._build_function = True

        return build_output
    
    def __setattr__(self, name: str, value: type | QueryBuilder) -> None:
        # All __setattr__ calls from within this class should be handled normally
        if inspect.stack()[1].filename == __file__:
            super().__setattr__(name, value)
            return

        # TODO: Support setting attributes to classes - perhaps this should update the
        #       resolved fields? It would allow for dynamic QueryBuilder creation.
        if type(self) == type:
            raise AttributeError("Cannot set attributes on a QueryBuilder class." \
                                 "Please create an instance of the class first.")
        if self._valid_field(name, value):
            self.build_fields = self.build_fields or {}
            self.build_fields[name] = value

    def _valid_field(self, name: str, value: type | QueryBuilder) -> bool:
        """Checks if the given field name and value is valid for this QueryBuilder.
        
        e.g.
        class Human(gqlrequests.QueryBuilder):
            id: int
            info: PersonalInfo

        human = Human(fields=[])
        infoObject = PersonalInfo(fields=["name"])

        human._valid_field("info", infoObject)  # True
        human._valid_field("info", PersonalInfo)  # True
        human._valid_field("info", str)  # False
        """
        if type(self) == type:
            raise AttributeError("Cannot set attributes on a QueryBuilder class." \
                                 "Please create an instance of the class first.")
        
        if not self._resolved_fields:
            return False

        if name not in self._resolved_fields:
            return False
        if value == self._resolved_fields[name]:
            return True
        if type(value) != type and isinstance(value, QueryBuilder):
            return type(value) == self._resolved_fields[name]
        return False