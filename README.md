# gqlrequests - Create requests to GraphQL APIs with no strings attached 😉

[![Pytests and Coverage](https://github.com/BeatsuDev/GraphQLRequests/actions/workflows/testing_and_coverage.yml/badge.svg)](https://github.com/BeatsuDev/GraphQLRequests/actions/workflows/testing_and_coverage.yml)
[![Code Quality](https://github.com/BeatsuDev/GraphQLRequests/actions/workflows/code_quality.yml/badge.svg)](https://github.com/BeatsuDev/GraphQLRequests/actions/workflows/code_quality.yml)
[![codecov](https://codecov.io/gh/BeatsuDev/GraphQLRequests/branch/master/graph/badge.svg?token=FBQKU5OEWT)](https://codecov.io/gh/BeatsuDev/GraphQLRequests)

Define GraphQL types in Python as classes, then use them to automatically build queries. Or even simpler;
gqlrequests will automatically build the classes for you given the api endpoint by using introspection! (Now that's awesome).
You no longer need to define your requests as multiline strings (hence no strings attached).

**These examples show what I envision this module to become.**
Examples of how it will work:

```py
import gqlrequests

class Episode(gqlrequests.QueryBuilder):
    name: str
    length: float

class Character(gqlrequests.QueryBuilder):
    name: str
    appearsIn: list[Episode]

print(Character)
# type Character {
#     name: String
#     appearsIn: [Episode]
# }
#

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

print(Character(indents=2).build()) # Default indent is 4
# {
#   name
#   appearsIn {
#     name
#     length
#   }
# }


getCharacter = Character()  # Function name is variable name by default
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

schema, types = gqlclient.introspect()
character_search_query = types.Character(func_name="findCharacter")

character = gqlclient.execute(character_search_query(name="Luke").build())
print(character.name)

# Asynchronous queries
RootQuery = schema.RootQuery
async def main():
    gqlclient = gqlrequests.AsyncClient(
        api_endpoint="api.example.com/gql",
        authorization="abcdefghijklmnopqrstuvwxyz"
    )

    queries = asyncio.gather(
        gqlclient.execute(RootQuery(fields=["character"]).build()),
        gqlclient.execute(RootQuery(fields=["episode"]).build())
    )

    character, episode = await queries

    # Or simply:
    character = await gqlclient.execute(RootQuery().build())

asyncio.run(main())
```

```py
"""Subscribing to a graphql websocket"""
import gqlrequests
import asyncio

schema, types = gqlrequests.introspect()
RootMutation = schema.RootMutation


# Example of how the type of RootMutation.live could look like:
#
# class LiveViewers(gqlrequests.QueryBuilder):
#     viewers: int
#     measurementTimeUnix: int


async def main():
    gqlclient = gqlrequests.Client(
        api_endpoint="api.example.com/gql",
        authorization="abcdefghijklmnopqrstuvwxyz"
    )

    query_string = RootMutation(fields=["live"]).build()

    async with gqlclient.subscribe(query_string) as subscription:
        async for data in subscription:
            assert isinstance(data, LiveViewers)

            print(data.viewers, data.measurementTimeUnix)
            if data.viewers < 10: break

asyncio.run(main())
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
