from gqlrequests.primitives import GraphQLPrimitive

class GraphQLType:
    def __str__(self):
        """Returns the type as it would be represented in GraphQL"""
        name = type(self).__name__
        attributes = [a for a in dir(self) if not a.startswith('__') and not a in dir(GraphQLType)]
        values = [getattr(self, a) for a in attributes]

        items = zip(attributes, values)

        output_string = f"type {name} {{\n"

        for field, field_value in items:
            def get_type(v):
                if isinstance(v, list):
                    if len(v) == 0:
                        return list.__name__
                    value = "[" + get_type(v[0]) + "]" 
                elif type(v) == type or type(v) == GraphQLType:
                    value = v.__name__
                else:
                    value = type(v).__name__
                return value

            output_string += f"\t{field}: {get_type(field_value)}\n"

        return output_string + "}"

    def query(self, *args, indent=4, recursion_depth=1):
        attributes_before_filter = [a for a in dir(self) if not a.startswith('__') and not a in dir(GraphQLType)]
        attributes = [a for a in attributes_before_filter if a in args] if len(args) > 0 else attributes_before_filter
        values = [getattr(self, a) for a in attributes]

        items = zip(attributes, values)
        
        output_string = "{\n"
        pre_spaces = " "*(indent*recursion_depth)

        for k, v in items:
            if isinstance(v, list):
                output_string += pre_spaces + k + " " + v[0].query(v[0], indent=indent, recursion_depth=recursion_depth+1)
                continue

            if issubclass(v, GraphQLPrimitive):
                output_string += pre_spaces + str(k) + "\n"
                continue

            output_string += pre_spaces + str(k) + " " + v.query(v, indent=indent, recursion_depth=recursion_depth+1)

        return output_string + " "*(indent*(recursion_depth-1)) + ("}\n" if recursion_depth > 1 else "}")