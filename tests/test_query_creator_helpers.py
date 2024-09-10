import sys
import enum
import pytest
import typing
import gqlrequests
from gqlrequests.query_creator import generate_fields, generate_query_string, generate_function_query_string
from gqlrequests.query_creator import FieldTypeEnum, resolve_type


# Generate fields functino

def test_generate_fields():
    correct_string = """
    id
    age
    money
    name
    company
"""[1:]
    
    fields = {
        "id": int,
        "age": int,
        "money": float,
        "name": str,
        "company": bool
    }
    assert generate_fields(fields) == correct_string

class AgeType(gqlrequests.QueryBuilder):
    age: int

def test_generate_fields_with_nested_query_builder():
    correct_string = """
    something {
        age
    }
"""[1:]

    fields = {
        "something": AgeType
    }

    assert generate_fields(fields) == correct_string

def test_generate_fields_with_nested_query_builder_instance():
    correct_string = """
    something {
        age
    }
"""[1:]

    fields = {
        "something": AgeType()
    }

    assert generate_fields(fields) == correct_string

def test_generate_fields_with_nested_function():
    correct_string = """
    innerFunc() {
        age
    }
"""[1:]

    fields = {
        "something": AgeType(func_name="innerFunc")()
    }

    assert generate_fields(fields) == correct_string

class InvalidType:
    pass

def test_generate_fields_with_invalid_type_raises_error():
    with pytest.raises(ValueError):
        generate_fields({"invalid": InvalidType})

# Generate query string function

def test_generate_query_string():
    correct_string = """
{
    id
    age
    money
    name
    company
}
"""[1:]
    
    fields = {
        "id": int,
        "age": int,
        "money": float,
        "name": str,
        "company": bool
    }
    assert generate_query_string(fields) == correct_string

def test_generate_query_string_with_no_fields_raises_error():
    fields = {}
    with pytest.raises(ValueError):
        generate_query_string(fields)

# Generate function query string function

def test_generate_function_query_string():
    correct_string = """
getSomething(id: 1, number: 3.14, name: \"John\", isCool: true) {
    id
    age
    money
    name
    company
}
"""[1:]
    args = {
        "id": 1,
        "number": 3.14,
        "name": "John",
        "isCool": True
    }

    fields = {
        "id": int,
        "age": int,
        "money": float,
        "name": str,
        "company": bool
    }

    assert generate_function_query_string("getSomething", args, fields) == correct_string

# Resolving types

def test_resolve_type_primitive():
    assert resolve_type(int) == (FieldTypeEnum.PRIMITIVE, int)
    assert resolve_type(float) == (FieldTypeEnum.PRIMITIVE, float)
    assert resolve_type(str) == (FieldTypeEnum.PRIMITIVE, str)
    assert resolve_type(bool) == (FieldTypeEnum.PRIMITIVE, bool)

def test_resolve_type_enum():
    class TestEnum(enum.Enum):
        VALUE = 1

    assert resolve_type(TestEnum) == (FieldTypeEnum.ENUM, TestEnum)

def test_resolve_type_query_builder_class():
    class TestQueryBuilder(gqlrequests.QueryBuilder):
        name: str

    assert resolve_type(TestQueryBuilder) == (FieldTypeEnum.QUERY_BUILDER_CLASS, TestQueryBuilder)

def test_resolve_type_query_builder_instance():
    class TestQueryBuilder(gqlrequests.QueryBuilder):
        name: str

    instance = TestQueryBuilder()
    assert resolve_type(instance) == (FieldTypeEnum.QUERY_BUILDER_INSTANCE, instance)

# Resolving list types

@pytest.mark.skipif(sys.version_info < (3, 9), reason="Python 3.9 syntax")
def test_resolve_list_field_python_39():
    class Test:
        age: list[list[list[int]]]
    
    hints = typing.get_type_hints(Test)
    assert resolve_type(hints["age"]) == (FieldTypeEnum.PRIMITIVE, int)

def test_resolve_list_field_python_38():
    class Test:
        age: typing.List[typing.List[typing.List[int]]]
    
    hints = typing.get_type_hints(Test)
    assert resolve_type(hints["age"]) == (FieldTypeEnum.PRIMITIVE, int)