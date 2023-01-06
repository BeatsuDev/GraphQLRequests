# gqlrequests - A Python library for creating GraphQL query easier!
Define GraphQL types in Python, then use them to build queries super easy. Supports dataclasses and
graphql-core schemas too! Example of how it will work:

**Note that these examples are the end goal and very few features have been developed yet!**
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
#     appearsIn: [Episode]
#     name: String
# }
#

print(gqlrequests.Query(Character))
# {
#     appearsIn {
#         name
#         length
#     }
#     name
# } 

print(gqlrequests.Query(Character, fields=["name"]))
# {
#     name
# } 

print(gqlrequests.Query(Character, indent=2)) # Default indent is 4
# {
#   appearsIn {
#     name
#     length
#   }
#   name
# }

print(gqlrequests.QueryMethod("get_character", Character, args={"name": "Luke"}))
# get_character(name: "Luke") {
#     appearsIn {
#         name
#         length
#     }
#     name
# }

print(gqlrequests.Query(
    Character,
    fields = [
        "name", 
        gqlrequests.QueryMethod(
            "appearsIn",
            Episode,
            args = {"minLength": 5}
        )
    ]
))
# {
#     appearsIn(minLength: 5) {
#         name
#         length
#     }
#     name
# } 
```
Future possible implementations:
```py
import gqlrequests
import asyncio

@dataclass
class Episode:
    name: str
    length: float

@dataclass
class Character:
    name: str
    appearsIn: list[Episode]


gqlclient = gqlrequests.Client(
    api_endpoint="api.example.com/gql",
    authorization="abcdefghijklmnopqrstuvwxyz"
)

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