import pytest
import gqlrequests

class EveryType(gqlrequests.QueryBuilder):
    id: int
    age: int
    money: float
    name: str
    company: bool
    
def test_primtives_only_query_build():
    correct_string = """
{
    id
    age
    money
    name
    company
}
"""[1:]
    every_type = EveryType().build()
    assert str(every_type) == correct_string

def test_setting_valid_property():
    correct_string = """
{
    id
    money
    name
    company
}
"""[1:]
    every_type = EveryType(fields=[])  # No fields are selected
    print(every_type.build_fields)
    every_type.id = int
    every_type.money = float
    every_type.name = str
    every_type.company = bool
    assert every_type.build() == correct_string

@pytest.mark.skip(reason="Not implemented yet")
def test_setting_invalid_property():
    every_type = EveryType(fields=[])  # No fields are selected
    
    with pytest.raises(AttributeError) as e:
        every_type.invalid = str
    
    assert "invalid" in str(e.value).lower()

@pytest.mark.skip(reason="Not implemented yet")
def test_setting_invalid_property_type():
    every_type = EveryType(fields=[])  # No fields are selected
    
    with pytest.raises(TypeError) as e:
        every_type.id = str
    
    assert "id" in str(e.value).lower()
    assert "int" in str(e.value).lower()
    assert "str" in str(e.value).lower()


class NestedType(gqlrequests.QueryBuilder):
    id: int
    age: int
    something: EveryType

@pytest.mark.skip(reason="Not implemented yet")
def test_setting_function_as_property():
    nested_type = NestedType(fields=[])
    nested_type.something = EveryType(fields=["id"])(test=5)

    correct_string = """
{
    something(test: 5) {
        id
    }
}
"""
    assert str(nested_type) == correct_string