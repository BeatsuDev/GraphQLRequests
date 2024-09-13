from typing import Type

from pydantic import BaseModel

from .builder import QueryBuilder


def from_pydantic(model: Type[BaseModel]) -> Type[QueryBuilder]:
    return type(model.__name__, (QueryBuilder,), {"__annotations__": model.__annotations__})