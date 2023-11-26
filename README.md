# gqlrequests - Create requests to GraphQL APIs with no strings attached 😉
[![Pytests and Coverage](https://github.com/BeatsuDev/GraphQLRequests/actions/workflows/testing_and_coverage.yml/badge.svg)](https://github.com/BeatsuDev/GraphQLRequests/actions/workflows/testing_and_coverage.yml)
[![Code Quality](https://github.com/BeatsuDev/GraphQLRequests/actions/workflows/code_quality.yml/badge.svg)](https://github.com/BeatsuDev/GraphQLRequests/actions/workflows/code_quality.yml)
[![codecov](https://codecov.io/gh/BeatsuDev/GraphQLRequests/branch/master/graph/badge.svg?token=FBQKU5OEWT)](https://codecov.io/gh/BeatsuDev/GraphQLRequests)

Define GraphQL types in Python as classes, then use them to automatically build queries. Or even simpler;
gqlrequests will automatically build the classes for you given the api endpoint by using introspection! (Now that's awesome).
You no longer need to define your requests as multiline strings (hence no strings attached).

**These examples show what I envision this module to become. Very few of these features have been developed yet, but I'm getting to it when I have time!**
Examples of how it will work:
```py
from dataclasses import dataclass
import gqlrequests

class Episode(gqlrequests.Type):
    name: str
    length: float

class Character(gqlrequests.Type):
    name: str
    appearsIn: list[Episode]

print(Character)
# type Character {
#     name: String
#     appearsIn: [Episode]
# }
#

print(gqlrequests.create_query(Character))
# {
#     name
#     appearsIn {
#         name
#         length
#     }
# } 

print(gqlrequests.create_query(Character, fields=["name"]))
# {
#     name
# } 

print(gqlrequests.create_query(Character, indents=2)) # Default indent is 4
# {
#   name
#   appearsIn {
#     name
#     length
#   }
# }

print(gqlrequests.create_query_method("get_character", Character, args={"name": "Luke"}))
# get_character(name: "Luke") {
#     name
#     appearsIn {
#         name
#         length
#     }
# }

appearsIn = gqlrequests.create_query_method("appearsIn", Episode, args = {"minLength": 5})

print(gqlrequests.create_query(
    Character,
    fields = [
        "name",
        appearsIn
    ]
))
# {
#     name
#     appearsIn(minLength: 5) {
#         name
#         length
#     }
# } 
```
Interacting with a GraphQL endpoint (gql already does this, but this would be nicer imo):
```py
import gqlrequests
import asyncio

# Normal query
gqlclient = gqlrequests.Client(
    api_endpoint="api.example.com/gql",
    authorization="abcdefghijklmnopqrstuvwxyz"
)

RootQuery = gqlclient.introspect()
Character, Episode = RootQuery.Character, RootQuery.Episode

character = gqlclient.query(gqlrequests.create_query(Character))
assert isinstance(character, Character)

# Asynchronous queries 
async def main():
    gqlclient = gqlrequests.AsyncClient(
        api_endpoint="api.example.com/gql",
        authorization="abcdefghijklmnopqrstuvwxyz"
    )

    queries = asyncio.gather(
        gqlclient.query(gqlrequests.create_query(Character)),
        gqlclient.query(gqlrequests.create_query(Episode))
    )

    character, episode = await queries

    assert isinstance(character, Character)
    assert isinstance(episode, Episode)

    # Or simply:
    character = await gqlclient.query(gqlrequests.create_query(Character))

asyncio.run(main())
```
```py
"""Subscribing to a graphql websocket"""
import gqlrequests
import asyncio


@dataclass
class LiveViewers:
    viewers: int
    measurementTimeUnix: int


async def main():
    gqlclient = gqlrequests.Client(
        api_endpoint="api.example.com/gql",
        authorization="abcdefghijklmnopqrstuvwxyz"
    )

    query = gqlrequests.create_query(LiveViewers)
    async with gqlclient.subscribe(query) as subscription:
        async for data in subscription:
            assert isinstance(data, LiveViewers)

            print(data.viewers, data.measurementTimeUnix)
            if data.viewers < 10: break

asyncio.run(main())
```

## Edge cases
Some attributes are reserved keywords in Python, such as `from`, `is` and `not`. These cannot be reference to
by property like this: `some_query_result.from`. Therefore for now, this edge case will be solved by using this
optional syntax:

```py
import gqlrequests
import asyncio

class Character(gqlrequests.Type):
    name: str
    appearsIn: list[Episode]

# gqlrequests.add_field(Type, field_name, type)
gqlrequests.add_field(Character, "from", str)

character = gqlrequests.create_query(Character)
character_from = character["from"]
```