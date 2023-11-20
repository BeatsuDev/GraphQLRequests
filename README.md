# gqlrequests - Create requests to GraphQL APIs with no strings attached 😉
[![Pytests and Coverage](https://github.com/BeatsuDev/GraphQLRequests/actions/workflows/testing_and_coverage.yml/badge.svg)](https://github.com/BeatsuDev/GraphQLRequests/actions/workflows/testing_and_coverage.yml)
[![Code Quality](https://github.com/BeatsuDev/GraphQLRequests/actions/workflows/code_quality.yml/badge.svg)](https://github.com/BeatsuDev/GraphQLRequests/actions/workflows/code_quality.yml)
[![codecov](https://codecov.io/gh/BeatsuDev/GraphQLRequests/branch/master/graph/badge.svg?token=FBQKU5OEWT)](https://codecov.io/gh/BeatsuDev/GraphQLRequests)

Define GraphQL types in Python as dataclasses, then use them to automatically build queries. Or even simpler;
gqlrequests will automatically build the dataclasses for you given the api endpoint by using introspection! (Now that's awesome).
You no longer need to define your requests as multiline strings - you can store and manipulate them as dataclasses (hence no strings attached).

**These examples show what I envision this module to become. Very few of these features have been developed yet, but I'm getting to it when I have time!**
Examples of how it will work:
```py
from dataclasses import dataclass
import gqlrequests

@dataclass
class Episode:
    name: str
    length: float

@dataclass
class Character:
    name: str
    appearsIn: list[Episode]

print(gqlrequests.Schema(Character))
# type Character {
#     name: String
#     appearsIn: [Episode]
# }
#

print(gqlrequests.Query(Character))
# {
#     name
#     appearsIn {
#         name
#         length
#     }
# } 

print(gqlrequests.Query(Character, fields=["name"]))
# {
#     name
# } 

print(gqlrequests.Query(Character, indents=2)) # Default indent is 4
# {
#   name
#   appearsIn {
#     name
#     length
#   }
# }

print(gqlrequests.QueryMethod("get_character", Character, args={"name": "Luke"}))
# get_character(name: "Luke") {
#     name
#     appearsIn {
#         name
#         length
#     }
# }

appearsIn = gqlrequests.QueryMethod(
    "appearsIn",
    Episode,
    args = {"minLength": 5}
)

print(gqlrequests.Query(
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
Interacting with a GraphQL endpoint:
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

character = gqlclient.query(gqlrequests.Query(Character))
assert isinstance(character, Character)

# Asynchronous queries 
async def main():
    gqlclient = gqlrequests.AsyncClient(
        api_endpoint="api.example.com/gql",
        authorization="abcdefghijklmnopqrstuvwxyz"
    )

    queries = asyncio.gather(
        gqlclient.query(gqlrequests.Query(Character)),
        gqlclient.query(gqlrequests.Query(Episode))
    )

    character, episode = await queries

    assert isinstance(character, Character)
    assert isinstance(episode, Episode)

    # Or simply:
    character = await gqlclient.query(gqlrequests.Query(Character))

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

    query = gqlrequests.Query(LiveViewers)
    async with gqlclient.subscribe(query) as subscription:
        async for data in subscription:
            assert isinstance(data, LiveViewers)

            print(data.viewers, data.measurementTimeUnix)
            if data.viewers < 10: break

asyncio.run(main())
```
