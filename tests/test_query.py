from dataclasses import dataclass
from typing import List

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
    {
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
