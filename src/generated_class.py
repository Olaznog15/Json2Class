from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class DefaultClassSub0:
    street: str = '123 Main St'
    city: str = 'Anytown'
    zipCode: str = '12345'

    def to_dict(self) -> Dict[str, Any]:
        result = dict()
        for key in self.__dataclass_fields__:
            value = getattr(self, key)
            if isinstance(value, list):
                result[key] = [item.to_dict() if hasattr(item, 'to_dict') else item for item in value]
            elif hasattr(value, 'to_dict'):
                result[key] = value.to_dict()
            else:
                result[key] = value
        return result

@dataclass
class DefaultClassSub1:
    createdAt: str = '2023-01-01'
    tags: List[str] = field(default_factory=lambda: ['user', 'active'])

    def to_dict(self) -> Dict[str, Any]:
        result = dict()
        for key in self.__dataclass_fields__:
            value = getattr(self, key)
            if isinstance(value, list):
                result[key] = [item.to_dict() if hasattr(item, 'to_dict') else item for item in value]
            elif hasattr(value, 'to_dict'):
                result[key] = value.to_dict()
            else:
                result[key] = value
        return result

@dataclass
class DefaultClassSub2:
    id: int = 1
    description: str = 'First item'
    value: float = 100.5
    active: bool = True

    def to_dict(self) -> Dict[str, Any]:
        result = dict()
        for key in self.__dataclass_fields__:
            value = getattr(self, key)
            if isinstance(value, list):
                result[key] = [item.to_dict() if hasattr(item, 'to_dict') else item for item in value]
            elif hasattr(value, 'to_dict'):
                result[key] = value.to_dict()
            else:
                result[key] = value
        return result

@dataclass
class DefaultClass:
    name: str = 'John Doe'
    age: int = 30
    isActive: bool = True
    address: DefaultClassSub0 = field(default_factory=lambda: DefaultClassSub0())
    hobbies: List[str] = field(default_factory=lambda: ['reading', 'coding'])
    metadata: DefaultClassSub1 = field(default_factory=lambda: DefaultClassSub1())
    numItems: int = 2
    items: List[DefaultClassSub2] = field(default_factory=lambda: [{'id': 1, 'description': 'First item', 'value': 100.5, 'active': True}, {'id': 2, 'description': 'Second item', 'value': 200.0, 'active': False}])

    def to_dict(self) -> Dict[str, Any]:
        result = dict()
        for key in self.__dataclass_fields__:
            value = getattr(self, key)
            if isinstance(value, list):
                result[key] = [item.to_dict() if hasattr(item, 'to_dict') else item for item in value]
            elif hasattr(value, 'to_dict'):
                result[key] = value.to_dict()
            else:
                result[key] = value
        return result
