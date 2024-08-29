"""Contains abstract classes to be inherited by classes with types hints.
These are then use to build GraphQL query strings in a Pythonic way."""

from __future__ import annotations

import abc
import inspect
import typing
from typing import Dict, List

from gqlrequests.query_creator import generate_function_query_string, generate_query_string


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

    def __init__(self, fields: List[str] | None = None, func_name: str | None = None) -> None:
        self.build_fields: Dict[str, type | QueryBuilder] = {}
        self._resolved_fields = typing.get_type_hints(self)
        if not self._resolved_fields:
            raise ValueError("A QueryBuilder must have type hints to build a query.")
        
        if fields is None:
            fields = list(self._resolved_fields.keys())
        
        self.func_name = func_name
        self.build_fields = { key: self._resolved_fields[key] for key in fields }

    def build(self, indent_size: int = 4, start_indents: int = 0) -> str:
        """Generates a GraphQL query string based on the fields set in the
        builder."""
        if not self.build_fields:
            raise ValueError("No fields were selected for the query builder. Cannot build an empty query.")

        if self._build_function:
            if not self.func_name:
                raise ValueError(f"Cannot build function query for {__name__}. Function name is missing.")
            return generate_function_query_string(self.func_name, self.func_args, self.build_fields, indent_size, start_indents)
        return generate_query_string(self.build_fields, indent_size, start_indents)

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