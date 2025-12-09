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
    id: str                          # unique car identifier
    direction: Direction             # where the car is coming from
    position: float                  # distance traveled along the lane
    speed: float                     # current speed value
    committed: bool                  # True once the car has passed the stop line
    color: Tuple[int, int, int]      # RGB color of the car
    is_vip: bool = False             # True for emergency vehicles (ambulance/police/fire)
