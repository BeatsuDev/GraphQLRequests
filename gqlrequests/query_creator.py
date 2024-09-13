from __future__ import annotations

import enum
import inspect
import sys
from typing import TYPE_CHECKING, Dict, Tuple, Type, _GenericAlias  # type: ignore

import gqlrequests

if sys.version_info >= (3, 9):
    from typing import GenericAlias  # type: ignore

if TYPE_CHECKING:
    from gqlrequests.builder import QueryBuilder  # pragma: no cover


class FieldTypeEnum(enum.Enum):
    PRIMITIVE = 1
    ENUM = 2
    QUERY_BUILDER_CLASS = 3
    QUERY_BUILDER_INSTANCE = 4


def generate_function_query_string(func_name: str, args: Dict[str, str | int | float | bool], fields: Dict[str, type | QueryBuilder | Type[QueryBuilder]], indent_size: int = 4, start_indents: int = 0) -> str:
    """Generates a GraphQL query string for a function with arguments."""
    query_string = func_name + "("

    processed_args = []
    for key, value in args.items():
        if isinstance(value, str):
            processed_args.append(f"{key}: \"{value}\"")
        elif isinstance(value, bool):
            processed_args.append(f"{key}: {str(value).lower()}")
        else:
            processed_args.append(f"{key}: {value}")
    return query_string + ", ".join(processed_args) + ") " + generate_query_string(fields, indent_size, start_indents)

def generate_query_string(fields: Dict[str, type | QueryBuilder | Type[QueryBuilder]], indent_size: int = 4, start_indents: int = 0) -> str:
    """Generates a GraphQL query string based on the fields set in the builder."""
    if len(fields.keys()) == 0:
        raise ValueError("No fields were selected for the query builder.")
    build_output = "{\n"
    build_output += generate_fields(fields, indent_size, start_indents)
    build_output += " " * start_indents + "}\n"
    return build_output

def generate_fields(fields: Dict[str, type | QueryBuilder | Type[QueryBuilder]], indent_size: int = 4, start_indents: int = 0) -> str:
    """Generates a string of the fields of a GraphQL query."""
    string_output = ""
    whitespaces = " " * start_indents + " " * indent_size
    
    for field, field_type_hint in fields.items():
        field_type_type, field_type = resolve_type(field_type_hint)

        if field_type_type in {FieldTypeEnum.PRIMITIVE, FieldTypeEnum.ENUM}:
            string_output += whitespaces + field + "\n"
        
        elif field_type_type == FieldTypeEnum.QUERY_BUILDER_CLASS:
            string_output += whitespaces + field + " " + field_type().build(indent_size, len(whitespaces))  # type: ignore

        elif field_type_type == FieldTypeEnum.QUERY_BUILDER_INSTANCE:
            if field_type.get("build_function"):  # type: ignore
                string_output += whitespaces + field_type.build(indent_size, len(whitespaces))  # type: ignore
            else:
                string_output += whitespaces + field + " " + field_type.build(indent_size, len(whitespaces))  # type: ignore

        else:
            # This error should already be caught in the resolve_type function
            raise ValueError(f"Invalid field type: {field_type}")  # pragma: no cover

    return string_output

def resolve_type(type_hint: type | enum.Enum | QueryBuilder | Type[QueryBuilder]) -> Tuple[FieldTypeEnum, type | enum.Enum | QueryBuilder | Type[QueryBuilder]]:
    primitives = { int, float, str, bool }

    # Primitive
    if type_hint in primitives or type_hint in (enum.Enum, enum.EnumMeta):
        return (FieldTypeEnum.PRIMITIVE, type_hint)
    
    # Enum
    if inspect.isclass(type_hint) and issubclass(type_hint, enum.Enum) or \
        not inspect.isclass(type_hint) and isinstance(type_hint, enum.Enum):
        return (FieldTypeEnum.ENUM, type_hint)
    
    # list[] in python 3.8 is NOT a class, but an instance of _GenericAlias
    # list[] in python 3.10 is the class AND an instance of GenericAlias (???? 
    #   inspect.isclass(list[int]) and isinstance(list[int], GenericAlias) == True)
    # list[] in python 3.12 is NOT a class, but an instance of GenericAlias...
    is_generic_alias = False
    if sys.version_info >= (3, 9):
        is_generic_alias = isinstance(type_hint, GenericAlias) or isinstance(type_hint, _GenericAlias)
    else:
        is_generic_alias = isinstance(type_hint, _GenericAlias)  # pragma: no cover

    is_generic_alias_list = is_generic_alias and type_hint.__origin__ == list  # type: ignore
    is_just_list = inspect.isclass(type_hint) and type_hint == list

    if is_generic_alias_list or is_just_list:
        return resolve_type(type_hint.__args__[0])  # type: ignore

    # QueryBuilder class
    if inspect.isclass(type_hint) and issubclass(type_hint, gqlrequests.builder.QueryBuilder):
        return (FieldTypeEnum.QUERY_BUILDER_CLASS, type_hint)
    
    # QueryBuilder instance
    if not inspect.isclass(type_hint) and isinstance(type_hint, gqlrequests.builder.QueryBuilder):
        return (FieldTypeEnum.QUERY_BUILDER_INSTANCE, type_hint)
    
    raise ValueError(f"Invalid field type: {type_hint}")