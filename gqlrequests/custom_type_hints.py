from typing import Dict, Protocol


class DataclassType(Protocol):
    __name__: str
    __dataclass_fields__: Dict
