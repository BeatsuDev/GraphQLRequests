from pydantic import BaseModel

from .builder import QueryBuilder


def from_pydantic(model: type[BaseModel]):
    return type(model.__name__, (QueryBuilder,), {"__annotations__": model.__annotations__})