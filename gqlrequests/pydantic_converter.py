from pydantic import BaseModel

from typing import Type
from .builder import QueryBuilder


def from_pydantic(model: Type[BaseModel]):
    return type(model.__name__, (QueryBuilder,), {"__annotations__": model.__annotations__})