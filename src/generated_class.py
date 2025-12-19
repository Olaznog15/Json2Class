from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass(slots=True)
class Telemetry:
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
class GpsCoordinates:
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
class Coordinates:
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
class RoutePoint:
    id: str = 'WPT01'
    name: str = 'Barajas'
    coordinates: Coordinates = field(default_factory=lambda: Coordinates())

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
class Aeronautical:
    flightId: str = 'IB3456'
    aircraftModel: str = 'Airbus A350'
    status: str = 'in_flight'
    telemetry: Telemetry = field(default_factory=lambda: Telemetry())
    gpsCoordinates: GpsCoordinates = field(default_factory=lambda: GpsCoordinates())
    numberRoutePoints: int = 2
    routePoints: List[RoutePoint] = field(default_factory=lambda: [{'id': 'WPT01', 'name': 'Barajas', 'coordinates': {'lat': 40.4983, 'lon': -3.5676}}, {'id': 'WPT02', 'name': 'Zaragoza', 'coordinates': {'lat': 41.6488, 'lon': -0.8891}}])

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
