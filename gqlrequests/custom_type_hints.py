from typing import ClassVar, Dict, Protocol


class DataclassType(Protocol):
    __name__: str
    __dataclass_fields__: ClassVar[Dict]
