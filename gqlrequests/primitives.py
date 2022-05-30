class GraphQLPrimitive:
    def __str__(self):
        return type(self).__name__

class Int(GraphQLPrimitive): pass
class Float(GraphQLPrimitive): pass
class String(GraphQLPrimitive): pass
class Boolean(GraphQLPrimitive): pass
class ID(GraphQLPrimitive): pass
