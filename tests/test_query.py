from gqlrequests import GraphQLType
from gqlrequests.primitives import *


class EveryType(GraphQLType):
    id = ID
    age = Int 
    money = Float
    name = String
    company = Boolean

class NestedType(GraphQLType):
    id = ID
    age = Int
    something = EveryType

class ListedType(GraphQLType):
    id = ID
    names = [String]
    types = [EveryType]


def test_primitive_types():
    assert EveryType.query() == """
{
    age
    company
    id
    money
    name
}
"""[1:-1]

def test_indent():
    assert EveryType.query(indent=2) == """
{
  age
  company
  id
  money
  name
}
"""[1:-1]

def test_query_selection():
    assert EveryType.query("id", "age") == """
{
    age
    id
}
"""[1:-1]
    
def test_nested_types():
    assert NestedType.query() == """
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
    assert ListedType.query() == """
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