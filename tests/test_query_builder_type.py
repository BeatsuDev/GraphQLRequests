import pytest
import gqlrequests
import enum
from typing import List

class EveryType(gqlrequests.QueryBuilder):
    id: int
    age: int
    money: float
    name: str
    company: bool

def test_primitive_types():
    correct_string = """
{
    id
    age
    money
    name
    company
}
"""[1:]
    assert EveryType().build() == correct_string

def test_indent():
    correct_string = """
{
  id
  age
  money
  name
  company
}
"""[1:]
    assert EveryType().build(indent_size=2) == correct_string


def test_query_selection():
    correct_string = """
{
    id
    age
}
"""[1:]
    assert EveryType(fields=["id", "age"]).build() == correct_string

def test_start_indent():
    # Note that the first bracket is not indented. This is intentional because
    # it is meant to be used in as a field value in a query, where the first
    # bracket is only 1 whitespace away from the field name
    correct_string = """
{
    id
    age
    money
    name
    company
  }
"""[1:]
    assert EveryType().build(indent_size=2, start_indents=2) == correct_string

def test_selecting_no_fields_and_converting_to_string_raises_value_error():
    with pytest.raises(ValueError) as e:
        EveryType(fields=[]).build()

    assert "no fields" in str(e.value).lower()


class NestedType(gqlrequests.QueryBuilder):
    id: int
    age: int
    something: EveryType


def test_nested_indent():
    correct_string = """
{
  id
  age
  something {
    id
    age
    money
    name
    company
  }
}
"""[1:]
    assert NestedType().build(indent_size=2) == correct_string

def test_nested_types():
    correct_string = """
{
    id
    age
    something {
        id
        age
        money
        name
        company
    }
}
"""[1:]
    assert NestedType().build() == correct_string


class ListedType(gqlrequests.QueryBuilder):
    id: int
    names: List[str]
    types: List[EveryType]


@pytest.mark.skip(reason="Not implemented yet")
def test_listed_types():
    correct_string = """
{
    id
    names
    types {
        id
        age
        money
        name
        company
    }
}
"""
    assert ListedType().build() == correct_string


class SomeClass(gqlrequests.QueryBuilder):
    pass


class InvalidType(gqlrequests.QueryBuilder):
    invalidProperty: SomeClass

@pytest.mark.skip(reason="Not implemented yet")
def test_invalid_type_throws_value_error():
    with pytest.raises(ValueError) as e:
        InvalidType()

    # Ensure the error message contains the name of the invalid property 
    # and the name of the class - this is to help the user debug the issue
    assert "invalidProperty" in str(e.value) and "InvalidType" in str(e.value)


class DatatypeWithKeywordAsProperty(gqlrequests.QueryBuilder):
    type: str  # This is okay, because type is a reserved *function*, not keyword
    from_: str
    as_: int


@pytest.mark.skip(reason="Not implemented yet")
def test_keyword_as_property_gets_stripped_for_underscores():
    correct_string = """
{
    type
    from
    as
}
"""
    assert DatatypeWithKeywordAsProperty().build() == correct_string


class SomeEnumClass(enum.Enum):
    ONE = 1
    TWO = 2
    THREE = 3


class ClassWithEnumeratedFieldType(gqlrequests.QueryBuilder):
    enumerated: SomeEnumClass


def test_enumerated_field_type():
    correct_string = """
{
    enumerated
}
"""[1:]
    assert ClassWithEnumeratedFieldType().build() == correct_string
