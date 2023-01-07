from dataclasses import dataclass
from typing import List

from gqlrequests.query import Query
from gqlrequests.query_method import QueryMethod


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


def test_method_with_no_args():
    assert str(QueryMethod("methodName", EveryType)) == """
methodName() {
    id
    age
    money
    name
    company
}
"""[1:-1]


def test_method_with_int_args():
    assert str(QueryMethod("methodName", EveryType, args = {"test": 5})) == """
methodName(test: 5) {
    id
    age
    money
    name
    company
}
"""[1:-1]


def test_method_with_str_args():
    assert str(QueryMethod("methodName", EveryType, args = {"test": "name"})) == """
methodName(test: "name") {
    id
    age
    money
    name
    company
}
"""[1:-1]


def test_method_with_float_args():
    assert str(QueryMethod("methodName", EveryType, args = {"test": 3.14159})) == """
methodName(test: 3.14159) {
    id
    age
    money
    name
    company
}
"""[1:-1]


def test_method_with_bool_args():
    assert str(QueryMethod("methodName", EveryType, args = {"test": True})) == """
methodName(test: true) {
    id
    age
    money
    name
    company
}
"""[1:-1]


def test_query_selection():
    assert str(QueryMethod("methodName", EveryType, fields=["id", "age"])) == """
methodName() {
    id
    age
}
"""[1:-1]


def test_query_method_as_nested():
    assert str(Query(NestedType, fields = ["id", "age", QueryMethod("methodName", EveryType)])) == """
{
    id
    age
    methodName() {
        id
        age
        money
        name
        company
    }
}
"""[1:-1]
