from typing import Dict, Any
from .types import Type


class Space:
    def __init__(self):
        self.types: Dict[str, Type] = {}

    def add_type(self, name: str, type_obj: Type):
        self.types[name] = type_obj

    def get_type(self, name: str) -> Type:
        return self.types.get(name)


class Universe(Type):
    def __init__(self, level: int):
        self.level = level

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Universe) and self.level == other.level
