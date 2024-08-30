import pytest
import gqlrequests

class EveryType(gqlrequests.QueryBuilder):
    id: int
    age: int
    money: float
    name: str
    company: bool

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