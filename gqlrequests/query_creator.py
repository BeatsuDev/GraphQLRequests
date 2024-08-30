from __future__ import annotations

import enum
import inspect
from typing import Dict

import gqlrequests


def generate_function_query_string(func_name: str, args: Dict[str, str | int | float | bool], fields: Dict[str, type | gqlrequests.builder.QueryBuilder], indent_size: int = 4, start_indents: int = 0) -> str:
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

def generate_query_string(fields: Dict[str, type | gqlrequests.builder.QueryBuilder], indent_size: int = 4, start_indents: int = 0) -> str:
    """Generates a GraphQL query string based on the fields set in the builder."""
    if len(fields.keys()) == 0:
        raise ValueError("No fields were selected for the query builder.")
    build_output = "{\n"
    build_output += generate_fields(fields, indent_size, start_indents)
    build_output += " " * start_indents + "}\n"
    return build_output

def generate_fields(fields: Dict[str, type | gqlrequests.builder.QueryBuilder], indent_size: int = 4, start_indents: int = 0) -> str:
    """Generates a string of the fields of a GraphQL query."""
    string_output = ""
    whitespaces = " " * start_indents + " " * indent_size
    
    for field, field_type in fields.items():
        is_primitive = inspect.isclass(field_type) and field_type in (int, float, str, bool)
        is_enum = type(field_type) in (enum.Enum, enum.EnumMeta)
        is_query_builder_class = inspect.isclass(field_type) and issubclass(field_type, gqlrequests.builder.QueryBuilder)
        is_query_builder_instance = not inspect.isclass(field_type) and isinstance(field_type, gqlrequests.builder.QueryBuilder)

        if is_primitive or is_enum:
            string_output += whitespaces + field + "\n"
        
        elif is_query_builder_class:
            string_output += whitespaces + field + " " + field_type().build(indent_size, len(whitespaces))
        
        elif is_query_builder_instance:
            if field_type.get("build_function"):  # type: ignore
                string_output += whitespaces + field_type.build(indent_size, len(whitespaces))  # type: ignore
            else:
                string_output += whitespaces + field + " " + field_type.build(indent_size, len(whitespaces))  # type: ignore
        
        else:
            raise ValueError(f"Invalid field type: {field_type}")

    return string_output