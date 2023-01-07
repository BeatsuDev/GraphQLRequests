from dataclasses import dataclass
from typing import List

import pytest

from gqlrequests.query import Query


@dataclass
class EveryType:
    id: int
    age: int
    money: float
    name: str
    company: bool


@dataclass
class NestedType:
    id: int
    age: int
    something: EveryType


@dataclass
class ListedType:
    id: int
    names: List[str]
    types: List[EveryType]


class SomeClass:
    pass


@dataclass
class InvalidType:
    invalidProperty: SomeClass


@dataclass
class DatatypeWithKeywordAsProperty:
    type: str  # This is okay, because type is a reserved *function*, not keyword
    from_: str
    as_: int


def test_primitive_types():
    assert str(Query(EveryType)) == """
{
    id
    age
    money
    name
    company
}
"""[1:-1]


def test_indent():
    assert str(Query(EveryType, indents=2)) == """
{
  id
  age
  money
  name
  company
}
"""[1:-1]


def test_nested_indent():
    assert str(Query(NestedType, indents=2)) == """
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
"""[1:-1]


def test_query_selection():
    assert str(Query(EveryType, fields=["id", "age"])) == """
{
    id
    age
}
"""[1:-1]


def test_nested_types():
    assert str(Query(NestedType)) == """
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
"""[1:-1]


def test_listed_types():
    assert str(Query(ListedType)) == """
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
"""[1:-1]

def test_invalid_type_throws_value_error():
    with pytest.raises(ValueError) as e:
        str(Query(InvalidType))
    
    # Ensure the error message contains the name of the invalid property 
    # and the name of the class - this is to help the user debug the issue
    assert "invalidProperty" in str(e.value) and "InvalidType" in str(e.value)

def test_keyword_as_property_gets_stripped_for_underscores():
    assert str(Query(DatatypeWithKeywordAsProperty)) == """
{
    type
    from
    as
}
"""[1:-1]

def test_start_indent():
    # Note that the first bracket is not indented. This is intentional because
    # it is meant to be used in as a field value in a query, where the first
    # bracket is only 1 whitespace away from the field name
    assert str(Query(EveryType, indents=2, start_indent=2)) == """
{
    id
    age
    money
    name
    company
  }
"""[1:-1]