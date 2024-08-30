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

@pytest.mark.skip(reason="Not implemented yet")
def test_invalid_type_throws_value_error():
    with pytest.raises(ValueError) as e:
        InvalidType()

    # Ensure the error message contains the name of the invalid property 
    # and the name of the class - this is to help the user debug the issue
    assert "invalidProperty" in str(e.value) and "InvalidType" in str(e.value)