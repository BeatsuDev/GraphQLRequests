import pytest
import gqlrequests

def get_new_sometype():
    class SomeType(gqlrequests.QueryBuilder):
        id: int

    return SomeType

def test_adding_field_by_setattr():
    correct_string = """
{
    id
    name
}
"""[1:]
    SomeType = get_new_sometype()
    SomeType.name = str
    assert SomeType().build() == correct_string

def test_removing_field_by_setattr():
    correct_string = """
{
    id
}
"""[1:]
    SomeType = get_new_sometype()
    SomeType.name = None
    assert SomeType().build() == correct_string

def test_adding_field_by_add_field():
    correct_string = """
{
    id
    name
}
"""[1:]
    SomeType = get_new_sometype()
    SomeType.add_field("name", str)
    assert SomeType().build() == correct_string

def test_removing_field_by_remove_field():
    correct_string = """
{
    id
}
"""[1:]
    SomeType = get_new_sometype()
    SomeType.add_field("name", str)
    SomeType.remove_field("name")
    assert SomeType().build() == correct_string

def test_removing_invalid_field_just_does_nothing():
    correct_string = """
{
    id
}
"""[1:]
    SomeType = get_new_sometype()
    SomeType.remove_field("name")
    assert SomeType().build() == correct_string

def test_adding_existing_field_overwrites_type():
    correct_string = """
{
    id
    name
}
"""[1:]
    SomeType = get_new_sometype()
    
    SomeType.name = int
    assert SomeType()._resolved_fields["name"] == int

    SomeType.name = str
    assert SomeType().build() == correct_string
    assert SomeType()._resolved_fields["name"] == str

class SomeClass(gqlrequests.QueryBuilder):
    pass

class InvalidType(gqlrequests.QueryBuilder):
    invalidProperty: SomeClass

def test_invalid_type_throws_value_error():
    with pytest.raises(ValueError) as e:
        InvalidType().build()

        
def test_string_representation_of_class_shows_graphql_syntax():
    class EveryType(gqlrequests.QueryBuilder):
        id: int
        age: int
        money: float
        name: str
        company: bool

    correct_string = """
type EveryType {
    id: int
    age: int
    money: float
    name: str
    company: bool
}
"""[1:]
    assert str(EveryType) == correct_string

def test_string_representation_of_nested_class_shows_graphql_syntax():
    correct_string = """
type NestedType {
    something: SomethingType
}
"""[1:]
    class SomethingType(gqlrequests.QueryBuilder):
        id: int

    class NestedType(gqlrequests.QueryBuilder):
        something: SomethingType
    
    assert str(NestedType) == correct_string