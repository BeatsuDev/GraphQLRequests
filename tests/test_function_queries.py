import pytest
import gqlrequests


class EveryType(gqlrequests.QueryBuilder):
    id: int
    age: int
    money: float
    name: str
    company: bool

def test_method_with_no_args():
    correct_string = """
methodName() {
    id
    age
    money
    name
    company
}
"""[1:]
    every_type = EveryType(func_name="methodName")
    assert every_type().build() == correct_string

def test_method_with_int_args():
    correct_string = """
methodName(test: 5) {
    id
    age
    money
    name
    company
}
"""[1:]
    every_type = EveryType(func_name="methodName")
    assert every_type(test=5).build() == correct_string

def test_method_with_str_args():
    correct_string = """
methodName(test: "name") {
    id
    age
    money
    name
    company
}
"""[1:]
    every_type = EveryType(func_name="methodName")
    assert every_type(test="name").build() == correct_string

def test_method_with_float_args():
    correct_string = """
methodName(test: 3.14159) {
    id
    age
    money
    name
    company
}
"""[1:]
    every_type = EveryType(func_name="methodName")
    assert every_type(test=3.14159).build() == correct_string

def test_method_with_bool_args():
    correct_string = """
methodName(test: true) {
    id
    age
    money
    name
    company
}
"""[1:]
    every_type = EveryType(func_name="methodName")
    assert every_type(test=True).build() == correct_string

def test_method_with_multiple_args():
    correct_string = """
methodName(test: 5, test2: "name", test3: 3.14159, test4: true) {
    id
    age
    money
    name
    company
}
"""[1:]
    every_type = EveryType(func_name="methodName")
    assert every_type(test=5, test2="name", test3=3.14159, test4=True).build() == correct_string

def test_function_with_selected_fields():
    correct_string = """
methodName() {
    id
    age
}
"""[1:]
    every_type = EveryType(func_name="methodName", fields=["id", "age"])
    assert every_type().build() == correct_string 


class NestedType(gqlrequests.QueryBuilder):
    id: int
    age: int
    something: EveryType

@pytest.mark.xfail(reason="bug: nested types don't get generated")
def test_nested_type_function():
    correct_string = """
methodName() {
    id
    age
    something {
        id
        age
        money
        name
        company
    }
}
"""[1:]
    every_type = EveryType(func_name="methodName")
    print(every_type().build())
    assert every_type().build() == correct_string

def test_nested_function_call():
    correct_string = """
methodName() {
    id
    age
    something(test: 5) {
        id
        age
        money
        name
        company
    }
}
"""[1:]
    nested_type = NestedType(func_name="methodName")
    nested_type.something = EveryType(func_name="something")(test=5)
    assert nested_type().build() == correct_string