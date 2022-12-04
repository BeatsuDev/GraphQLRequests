from gqlrequests.primitives import GraphQLPrimitive

def get_type(v):
    """Get the GraphQL type of a variable.
    
    Example:
    
    class MyGraphQLType(GraphQLType):
        something = [Int]
        
    >>> get_type(MyGraphQLType.something)
    Int
    """
    # If the value is a list, we need to get the type of the first element
    if isinstance(v, list):
        # If the list is empty, return []
        if len(v) == 0: return "[]"
        # Otherwise, return the type of the first element
        return "[" + get_type(v[0]) + "]" 

    # If the value is a GraphQLType, return the class name. If the value is an uninitialized
    # class, also return the class name.
    if type(v) == type or type(v) == GraphQLType:
        return v.__name__

    return type(v).__name__

class GraphQLType:
    def __str__(self):
        """Returns the type as it would be represented in GraphQL"""
        name = type(self).__name__

        # Get all attributes defined by the user (which is not a magic function or an attribute
        # of the inherited GraphQLType class).
        attributes = [a for a in dir(self) if not a.startswith('__') and not a in dir(GraphQLType)]
        values = [getattr(self, a) for a in attributes]

        items = zip(attributes, values)

        # Build the string that will be outputted
        output_string = f"type {name} {{\n"
        for field, field_value in items:
            output_string += f"\t{field}: {get_type(field_value)}\n"

        return output_string + "}"

    @classmethod
    def query(cls, *args, indent=4, strip_underscores=False, recursion_depth=1):
        """A recursive method that returns the GraphQL type the way it would be queried for.
        
        :args *str: The fields of the type to include in the query.
        :indent int: The amount of spaces for each indent step
        :strip_underscores bool: Whether to strip underscores of attributes or not (this is to support name collisions in Python)
        :recursion_depth int: The depth in the recursion at which this
            method is called (used to track indentation spaces necessary)
        """
        attributes_before_filter = [a for a in dir(cls) if not a.startswith('__') and not a in dir(GraphQLType)]

        # Only include the fields that are in args. If args is empty, include all fields.
        attributes = [a for a in attributes_before_filter if a in args] if len(args) > 0 else attributes_before_filter
        values = [getattr(cls, a) for a in attributes]

        items = zip([(a.strip("_") if strip_underscores else a) for a in attributes], values)
        
        # Build the output string
        output_string = "{\n"
        pre_spaces = " "*(indent*recursion_depth)
        for k, v in items:
            output_string += pre_spaces + k

            if isinstance(v, list):
                if issubclass(v[0], GraphQLPrimitive):
                    output_string += "\n"
                    continue

                output_string += " " + v[0].query(indent=indent, strip_underscores=strip_underscores, recursion_depth=recursion_depth+1)
                continue

            if issubclass(v, GraphQLPrimitive):
                output_string += "\n"
                continue

            output_string += " " + v.query(indent=indent, strip_underscores=strip_underscores, recursion_depth=recursion_depth+1)

        return output_string + " "*(indent*(recursion_depth-1)) + ("}\n" if recursion_depth > 1 else "}")