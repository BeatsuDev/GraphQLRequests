# gqlrequests - Create requests to GraphQL APIs with no strings attached 😉

[![Pytests and Coverage](https://github.com/BeatsuDev/GraphQLRequests/actions/workflows/testing_and_coverage.yml/badge.svg)](https://github.com/BeatsuDev/GraphQLRequests/actions/workflows/testing_and_coverage.yml)
[![Code Quality](https://github.com/BeatsuDev/GraphQLRequests/actions/workflows/code_quality.yml/badge.svg)](https://github.com/BeatsuDev/GraphQLRequests/actions/workflows/code_quality.yml)
[![codecov](https://codecov.io/gh/BeatsuDev/GraphQLRequests/branch/main/graph/badge.svg?token=FBQKU5OEWT)](https://codecov.io/gh/BeatsuDev/GraphQLRequests)

Define GraphQL types in Python as classes or pydantic classes, then use them to automatically build queries. Or even simpler;
gqlrequests will automatically build the classes for you given the api endpoint by using introspection! (Now that's awesome).
You no longer need to define your requests as multiline strings (hence no strings attached).

## Examples of currently working features:

```py
import gqlrequests

class Episode(gqlrequests.QueryBuilder):
    name: str
    length: float

class Character(gqlrequests.QueryBuilder):
    name: str
    appearsIn: list[Episode]

print(Character().build())
# {
#     name
#     appearsIn {
#         name
#         length
#     }
# }

print(Character(fields=["name"]).build())
# {
#     name
# }

print(Character().build(indents=2)) # Default indent is 4
# {
#   name
#   appearsIn {
#     name
#     length
#   }
# }

getCharacter = Character(func_name="getCharacter")
print(getCharacter(name="Luke").build())
# getCharacter(name: "Luke") {
#     name
#     appearsIn {
#         name
#         length
#     }
# }

episode_func = Episode(func_name="appearsIn")

characters_query = Character()
characters_query.appearsIn = episode_func(minLength=5)

print(characters_query.build())
# {
#     name
#     appearsIn(minLength: 5) {
#         name
#         length
#     }
# }

from pydantic import BaseModel

class ExampleModel(BaseModel):
    age: int
    name: str

ExampleQueryBuilder = gqlrequests.from_pydantic(ExampleModel)

print(ExampleQueryBuilder().build())
```

## Edge cases

Some attributes are reserved keywords in Python, such as `from`, `is` and `not`. These cannot be referenced to
by property like this: `some_query_result.from`. This can be circumvented by adding leading or trailing underscores,
then passing the `strip_underscores` argument to the build method.

```py
class Time(gqlrequests.QueryBuilder):
    _from: int
    _to: int
    value: float

print(Time().build(strip_underscores=True))
# {
#     from
#     to
#     value
# }
```

## Other features that are not yet implemented:

```py
print(Character)
# type Character {
#     name: String
#     appearsIn: [Episode]
# }
#
```
