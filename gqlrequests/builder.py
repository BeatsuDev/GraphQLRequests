"""Contains abstract classes to be inherited by classes with types hints.
These are then use to build GraphQL query strings in a Pythonic way."""

from __future__ import annotations

import inspect
import typing
from types import SimpleNamespace
from typing import List

from gqlrequests.query_creator import generate_function_query_string, generate_query_string


class QueryBuilderMeta(type):
    def __new__(cls, name, bases, dct):
        new_class = super().__new__(cls, name, bases, dct)
        if not name == "QueryBuilder":
            new_class._resolved_fields = typing.get_type_hints(new_class)
        return new_class
    
    def __setattr__(cls, name, value):
        if name == "_resolved_fields":
            return super().__setattr__(name, value)
        try:
            old_fields = super().__getattribute__("_resolved_fields")
        except AttributeError:
            old_fields = {}

        if value is None:
            old_fields.pop(name, None)
        else:
            old_fields[name] = value

        super().__setattr__("_resolved_fields", old_fields)

class QueryBuilder(metaclass=QueryBuilderMeta):
    """An abstract class used to build GraphQL queries.

    This class should be inherited by a class with type hints and only
    supports single-leveled inheritance.

    Example usage:

        class EveryType(gqlrequests.QueryBuilder):
            id: int
            age: int
            money: float
            name: str
            company: bool

        EveryType.add_field("address", str)
        EveryType.remove_field("age")

        every_type = EveryType(fields=["id", "money", "name", "company"])
        graphql_query_string = every_type.build()

    """

    SUPPORTED_TYPES = (int, float, str, bool)

    def __init__(self, fields: List[str] | None = None, func_name: str | None = None) -> None:
        # Used to avoid calls to __setattr__ when setting attributes
        self._query_build_data = SimpleNamespace()

        # This will always be defined... Just need to help mypy out
        self._resolved_fields = getattr(self, "_resolved_fields", {})

        if fields is None:
            fields = list(self._resolved_fields.keys())
        
        self.set("fields_to_build", { key: self._resolved_fields[key] for key in fields })
        self.set("func_name", func_name)
        self.set("build_function", False)

    @classmethod
    def add_field(cls, field_name: str, field_type: type) -> None:
        cls._resolved_fields[field_name] = field_type

    @classmethod
    def remove_field(cls, field_name: str) -> None:
        cls._resolved_fields.pop(field_name, None)

    def set(self, name, value):
        setattr(self._query_build_data, name, value)

    def get(self, name):
        return getattr(self._query_build_data, name)

    def build(self, indent_size: int = 4, start_indents: int = 0, strip_undersores: bool = False) -> str:
        """Generates a GraphQL query string based on the fields set in the
        builder."""
        if not (fields_to_build := self.get("fields_to_build")):
            raise ValueError("No fields were selected for the query builder. Cannot build an empty query.")
        
        if strip_undersores:
            fields_to_build = { key.strip("_"): value for key, value in fields_to_build.items() }

        if self.get("build_function"):
            if not (func_name := self.get("func_name")):
                raise ValueError(f"Cannot build function query for {__name__}. Function name is missing.")
            return generate_function_query_string(func_name, self.get("func_args"), fields_to_build, indent_size, start_indents)
        return generate_query_string(fields_to_build, indent_size, start_indents)

    def __call__(self, **args) -> QueryBuilder:
        """After calling this method, the builder will build a function."""
        if not self._query_build_data.func_name:
            raise ValueError("No function name was set for this builder.")

        # TODO: Add support for non-primitive arguments
        for key, value in args.items():
            if type(value) not in self.SUPPORTED_TYPES:
                raise ValueError(
                    f"Function argument {key} of {self.get('func_name')} must be of"
                    f"the following types: {self.SUPPORTED_TYPES}"
                )

        self.set("func_args", args)
        self.set("build_function", True)

        return self

    def __setattr__(self, name: str, value: type | QueryBuilder | None) -> None:
        if name in {"_query_build_data", "_resolved_fields"}:
            return super().__setattr__(name, value)
        
        if self.__class__.__name__ == "QueryBuilder":
            raise AttributeError("Cannot set attributes on a QueryBuilder class." \
                                 "Make a class that inherits from QueryBuilder.")

        if inspect.isclass(self):
            pass  # This should be handled by the metaclass

        elif value is None:
            self._query_build_data.fields_to_build.pop(name, None)

        elif self.valid_field(name, value):
            self._query_build_data.fields_to_build[name] = value

        else:
            try:
                expected_type = self._resolved_fields[name]
                raise AttributeError(f"Cannot set {name} to {value}. Expected {expected_type}.")
            except KeyError:
                raise AttributeError(f"{name} is not a valid field on {self.__class__.__name__}.")

    def valid_field(self, name: str, value: type | QueryBuilder) -> bool:
        """Checks if the given field name and value is valid for this QueryBuilder.
        
        e.g.
        class Human(gqlrequests.QueryBuilder):
            id: int
            info: PersonalInfo

        human = Human(fields=[])
        infoObject = PersonalInfo(fields=["name"])

        human.valid_field("info", infoObject)  # True
        human.valid_field("info", PersonalInfo)  # True
        human.valid_field("info", str)  # False
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