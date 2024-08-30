import pytest
import gqlrequests

class EveryType(gqlrequests.QueryBuilder):
    id: int
    age: int
    money: float
    name: str
    company: bool

def test_selecting_fields_builds_only_selected_fields():
    correct_string = """
{
    id
    age
}
"""[1:]
    assert EveryType(fields=["id", "age"]).build() == correct_string

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
    every_type.id = int
    every_type.money = float
    every_type.name = str
    every_type.company = bool
    assert every_type.build() == correct_string

def test_setting_invalid_property():
    every_type = EveryType(fields=[])  # No fields are selected
    
    with pytest.raises(AttributeError) as e:
        every_type.invalid = str
    
    assert "invalid" in str(e.value).lower()

def test_setting_invalid_property_type():
    every_type = EveryType(fields=[])  # No fields are selected
    
    with pytest.raises(AttributeError) as e:
        every_type.id = str
    
    assert "id" in str(e.value).lower()
    assert "int" in str(e.value).lower()
    assert "str" in str(e.value).lower()
