import gqlrequests

from typing import List
from pydantic import BaseModel

class EveryTypeModel(BaseModel):
    id: int
    age: int
    money: float
    name: str
    company: bool

def test_create_everytype():
    correct_string = """
{
    id
    age
    money
    name
    company
}
"""[1:]
    EveryType = gqlrequests.from_pydantic(EveryTypeModel)
    assert EveryType().build() == correct_string


class NestedTypeModel(BaseModel):
    nested: EveryTypeModel

def test_create_nestedtype():
    correct_string = """
{
    nested {
        id
        age
        money
        name
        company
    }
}
"""[1:]
    NestedType = gqlrequests.from_pydantic(NestedTypeModel)
    assert NestedType().build() == correct_string


class ListTypeModel(BaseModel):
    nested: List[int]

def test_create_listtype():
    correct_string = """
{
    nested
}
"""[1:]
    ListType = gqlrequests.from_pydantic(ListTypeModel)
    assert ListType().build() == correct_string