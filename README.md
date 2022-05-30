# gqlrequests - A Python library for making GraphQL requests easier!
Define GraphQL types in Python, then use them to build queries super easy:
```py
from gqlrequests import GraphQLType
from gqlrequests.primitives import *

# All the primitive types available
# from gqlrequests.primitives import ID
# from gqlrequests.primitives import Int
# from gqlrequests.primitives import Float
# from gqlrequests.primitives import String
# from gqlrequests.primitives import Boolean


class Episode(GraphQLType):
    name = String
    length = Float

class Character(GraphQLType):
    name = String
    appearsIn = [Episode]

print(Character())
# type Character {
#     appearsIn: [Episode]
#     name: String
# }
#

print(Character().query())
# {
#     appearsIn {
#         name
#         length
#     }
#     name
# } 

print(Character().query("name"))
# {
#     name
# } 

print(Character().query(indent=2)) # Default indent is 4
# {
#   appearsIn {
#     name
#     length
#   }
#   name
# } 
```
