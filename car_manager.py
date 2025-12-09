# car_manager.py
import random
from typing import List, Dict

from models import Car, Direction, LightState


class CarManager:
    # Regular car colors
    CAR_COLORS = [
        (59, 130, 246),
        (239, 68, 68),
        (16, 185, 129),
        (245, 158, 11),
        (139, 92, 246),
        (236, 72, 153)
    ]

    # Special colors for VIP/emergency cars
    VIP_COLORS = [
        (255, 255, 255),    # white
        (0, 200, 255),      # bright blue
        (255, 0, 0)         # red
    ]

    VIP_SPAWN_PROB = 0.03  # probability of a random VIP spawn

    def __init__(self):
        # All active cars
        self.cars: List[Car] = []
        self.next_id = 0

        # Road layout values
        self.stop_line_position = 290
        self.intersection_end = 450
        self.max_speed = 0.4
        self.min_distance = 40  # minimum gap between cars

    def spawn_car(self, direction: Direction, force_vip: bool = False) -> None:
        """Creates a new car, sometimes VIP depending on probability or manual override."""

        # Decide if this will be a VIP car
        is_vip = force_vip or (random.random() < self.VIP_SPAWN_PROB)

        # Pick color depending on type
        color = random.choice(self.VIP_COLORS if is_vip else self.CAR_COLORS)

        # Create the car
        car = Car(
            id=f"car-{self.next_id}",
            direction=direction,
            position=0.0,
            speed=self.max_speed,
            committed=False,
            color=color,
            is_vip=is_vip
        )

        self.next_id += 1
        self.cars.append(car)

    def update_cars(self, get_light_state, delta_time: float) -> None:
        """Moves cars forward and applies stopping rules based on traffic lights."""

        cars_by_direction = self._group_cars_by_direction()

        for car in self.cars:
            light_state = get_light_state(car.direction)

            # Look for the next car ahead in the same lane
            cars_ahead = [
                c for c in cars_by_direction[car.direction]
                if c.position > car.position and c.position - car.position < 100
            ]
            cars_ahead.sort(key=lambda c: c.position)
            nearest_car_ahead = cars_ahead[0] if cars_ahead else None

            # Mark car as committed once past the intersection
            if car.position >= self.intersection_end:
                car.committed = True

            # If the car reaches the stop line and the light is green, it may pass
            elif car.position >= self.stop_line_position and not car.committed:
                if light_state == LightState.GREEN:
                    car.committed = True

            # Start with max allowed speed
            target_speed = self.max_speed

            # Adjust speed based on distance to the next car
            if nearest_car_ahead:
                distance = nearest_car_ahead.position - car.position

                if distance < self.min_distance:
                    target_speed = 0  # fully stop
                elif distance < self.min_distance * 2:
                    target_speed = self.max_speed * 0.5  # slow down

            # Apply stopping logic at red/yellow lights
            if not car.committed and light_state in [LightState.RED, LightState.YELLOW]:
                stop_pos = self.stop_line_position

                # Stay behind the car ahead
                if nearest_car_ahead:
                    stop_pos = min(stop_pos, nearest_car_ahead.position - self.min_distance)

                # If the car has reached its stopping position
                if car.position >= stop_pos:
                    car.position = stop_pos
                    target_speed = 0
                else:
                    # Smooth slow-down when approaching the stop line
                    distance_to_stop = stop_pos - car.position
                    if distance_to_stop < 80:
                        target_speed = min(target_speed, distance_to_stop / 10.0)

            # Smooth transition to target speed
            car.speed += (target_speed - car.speed) * 0.1

            # Move car
            car.position += car.speed * delta_time

    def _group_cars_by_direction(self) -> Dict[Direction, List[Car]]:
        """Groups cars by the direction of their lane."""
        return {
            Direction.NORTH: [c for c in self.cars if c.direction == Direction.NORTH],
            Direction.SOUTH: [c for c in self.cars if c.direction == Direction.SOUTH],
            Direction.EAST:  [c for c in self.cars if c.direction == Direction.EAST],
            Direction.WEST:  [c for c in self.cars if c.direction == Direction.WEST]
        }

    def get_queue_count(self, direction: Direction) -> int:
        """Counts cars waiting before the stop line."""
        return len([
            c for c in self.cars
            if c.direction == direction and
               c.position <= self.stop_line_position and
               not c.committed
        ])

    def get_vip_queue_count(self, direction: Direction) -> int:
        """Counts VIP/emergency vehicles waiting before the stop line."""
        return len([
            c for c in self.cars
            if c.direction == direction and
               c.is_vip and
               c.position <= self.stop_line_position and
               not c.committed
        ])

    def get_vip_directions_waiting(self) -> List[Direction]:
        """Returns a list of directions where VIP cars are currently waiting."""
        return [
            d for d in Direction
            if self.get_vip_queue_count(d) > 0
        ]

    def get_cars(self) -> List[Car]:
        """Returns the current list of active cars."""
        return self.cars

    def clear_cars(self) -> None:
        """Removes all cars from the simulation."""
        self.cars = []
