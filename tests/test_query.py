from dataclasses import dataclass

from gqlrequests import Query


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
    names: list[str]
    types: list[EveryType]


def test_primitive_types():
    assert str(Query(EveryType)) == """
{
    age
    company
    id
    money
    name
}
"""[1:-1]


def test_indent():
    assert str(Query(EveryType, indent=2)) == """
{
  age
  company
  id
  money
  name
}
"""[1:-1]


def test_query_selection():
    assert str(Query(EveryType, fields=["id", "age"])) == """
{
    age
    id
}
"""[1:-1]


def test_nested_types():
    assert str(Query(NestedType)) == """
{
    age
    id
    something {
        age
        company
        id
        money
        name
    }
}
"""[1:-1]


def test_listed_types():
    assert str(Query(ListedType)) == """
{
    id
    names
    types {
        age
        company
        id
        money
        name
    }
}
"""[1:-1]
