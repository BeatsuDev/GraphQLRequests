# gqlrequests - A Python library for making GraphQL requests easier!
Define GraphQL types in Python, then use them to build queries super easy:
```py
class Episode(GraphQLType):
    name = str
    length = float

class Character(GraphQLType):
    name = str
    appearsIn = [Episode]

print(Character)

print(Character.query())
# {
#     name
#     appearsIn {
#         name
#         length
#     }
# } 

print(Character.query("name"))
# {
#     name
# } 

print(Character.query(indent=2)) # Default indent is 4
# {
#   name
#   appearsIn {
#     name
#     length
#   }
# } 
```