from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass(slots=True)
class DefaultClassSub0:
    rotationAngle: float = 0.5
    pitch: float = 2.3
    roll: float = -1.2
    altitude: int = 32000
    speed: int = 480

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

@dataclass(slots=True)
class DefaultClassSub1:
    latitude: float = 40.4168
    longitude: float = -3.7038

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

@dataclass(slots=True)
class DefaultClassSub2Sub3:
    lat: float = 40.4983
    lon: float = -3.5676

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

@dataclass(slots=True)
class DefaultClassSub2:
    id: str = 'WPT01'
    name: str = 'Barajas'
    coordinates: DefaultClassSub2Sub3 = field(default_factory=lambda: DefaultClassSub2Sub3())

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

@dataclass(slots=True)
class DefaultClass:
    flightId: str = 'IB3456'
    aircraftModel: str = 'Airbus A350'
    status: str = 'in_flight'
    telemetry: DefaultClassSub0 = field(default_factory=lambda: DefaultClassSub0())
    gpsCoordinates: DefaultClassSub1 = field(default_factory=lambda: DefaultClassSub1())
    numberRoutePoints: int = 2
    routePoints: List[DefaultClassSub2] = field(default_factory=lambda: [{'id': 'WPT01', 'name': 'Barajas', 'coordinates': {'lat': 40.4983, 'lon': -3.5676}}, {'id': 'WPT02', 'name': 'Zaragoza', 'coordinates': {'lat': 41.6488, 'lon': -0.8891}}])

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
