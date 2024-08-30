import enum
import pytest
import gqlrequests

from typing import List


class EveryType(gqlrequests.QueryBuilder):
    id: int
    age: int
    money: float
    name: str
    company: bool
    
def test_class_with_only_primitives_builds_correctly():
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
    
def test_setting_indent_builds_correctly():
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

def test_builder_with_start_indents_set_builds_correctly():
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

def test_selecting_no_fields_and_building_raises_value_error():
    with pytest.raises(ValueError) as e:
        EveryType(fields=[]).build()

    assert "no fields" in str(e.value).lower()


class NestedType(gqlrequests.QueryBuilder):
    id: int
    age: int
    something: EveryType

def test_nested_type_builds_correctly():
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


def test_nested_indent_builds_correctly():
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


class ListedType(gqlrequests.QueryBuilder):
    id: int
    names: List[str]
    types: List[EveryType]


@pytest.mark.skip(reason="Not implemented yet")
def test_class_with_list_type_as_field_builds_correctly():
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

class SomeEnumClass(enum.Enum):
    ONE = 1
    TWO = 2
    THREE = 3


class ClassWithEnumeratedFieldType(gqlrequests.QueryBuilder):
    enumerated: SomeEnumClass


def test_class_with_enum_field_type_builds_correctly():
    correct_string = """
{
    enumerated
}
"""[1:]
    assert ClassWithEnumeratedFieldType().build() == correct_string


class DatatypeWithKeywordAsProperty(gqlrequests.QueryBuilder):
    type: str  # This is okay, because type is a reserved *function*, not keyword
    from_: str
    as_: int


def test_keywords_as_field_name_gets_stripped_for_underscores():
    correct_string = """
{
    type
    from
    as
}
"""[1:]
    assert DatatypeWithKeywordAsProperty().build(strip_undersores=True) == correct_string
