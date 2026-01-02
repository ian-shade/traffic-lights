# models.py
from enum import Enum
from dataclasses import dataclass
from typing import Tuple


# Basic directions used by cars and traffic lights
class Direction(Enum):
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"


# Light states for each traffic light
class LightState(Enum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"


# Represents a single car in the simulation
@dataclass
class Car:
    id: str
    direction: Direction
    position: float
    speed: float
    committed: bool
    color: Tuple[int, int, int]
    is_vip: bool = False
    spawn_time: float = 0.0
