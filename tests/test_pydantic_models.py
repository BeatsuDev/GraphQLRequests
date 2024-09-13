import gqlrequests
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