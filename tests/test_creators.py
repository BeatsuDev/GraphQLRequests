import gqlrequests
from gqlrequests.query_creator import generate_fields, generate_query_string, generate_function_query_string


def test_generate_fields():
    correct_string = """
    id
    age
    money
    name
    company
"""[1:]
    
    fields = {
        "id": int,
        "age": int,
        "money": float,
        "name": str,
        "company": bool
    }
    assert generate_fields(fields) == correct_string

def test_generate_query_string():
    correct_string = """
{
    id
    age
    money
    name
    company
}
"""[1:]
    
    fields = {
        "id": int,
        "age": int,
        "money": float,
        "name": str,
        "company": bool
    }
    assert generate_query_string(fields) == correct_string

def test_generate_function_query_string():
    correct_string = """
getSomething(id: 1, number: 3.14, name: \"John\", isCool: true) {
    id
    age
    money
    name
    company
}
"""[1:]
    args = {
        "id": 1,
        "number": 3.14,
        "name": "John",
        "isCool": True
    }

    fields = {
        "id": int,
        "age": int,
        "money": float,
        "name": str,
        "company": bool
    }

    assert generate_function_query_string("getSomething", args, fields) == correct_string