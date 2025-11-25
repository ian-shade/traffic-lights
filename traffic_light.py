import pygame
import sys
import random
import math
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Tuple
from datetime import datetime

pygame.init()

class Direction(Enum):
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"

class LightState(Enum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"

@dataclass
class Car:
    id: str
    direction: Direction
    position: float
    speed: float
    committed: bool
    color: Tuple[int, int, int]

class TrafficController:
    def __init__(self):
        self.current_phase = "NS"
        self.phase_start_time = datetime.now()
        self.green_duration = 30000
        self.yellow_duration = 3000
        self.min_green_duration = 10000

        self.ns_state = LightState.GREEN
        self.ew_state = LightState.RED

    def update(self, queue_stats: Dict[Direction, int]) -> None:
        elapsed = (datetime.now() - self.phase_start_time).total_seconds() * 1000

        if self.current_phase == "NS":
            if self.ns_state == LightState.GREEN:
                should_switch = self._should_switch_phase(queue_stats, elapsed)
                if elapsed >= self.green_duration or should_switch:
                    self.ns_state = LightState.YELLOW
                    self.phase_start_time = datetime.now()
            elif self.ns_state == LightState.YELLOW:
                if elapsed >= self.yellow_duration:
                    self.ns_state = LightState.RED
                    self.ew_state = LightState.GREEN
                    self.current_phase = "EW"
                    self.phase_start_time = datetime.now()
        else:
            if self.ew_state == LightState.GREEN:
                should_switch = self._should_switch_phase(queue_stats, elapsed)
                if elapsed >= self.green_duration or should_switch:
                    self.ew_state = LightState.YELLOW
                    self.phase_start_time = datetime.now()
            elif self.ew_state == LightState.YELLOW:
                if elapsed >= self.yellow_duration:
                    self.ew_state = LightState.RED
                    self.ns_state = LightState.GREEN
                    self.current_phase = "NS"
                    self.phase_start_time = datetime.now()

    def _should_switch_phase(self, queue_stats: Dict[Direction, int], elapsed: float) -> bool:
        if elapsed < self.min_green_duration:
            return False

        ns_count = queue_stats[Direction.NORTH] + queue_stats[Direction.SOUTH]
        ew_count = queue_stats[Direction.EAST] + queue_stats[Direction.WEST]

        if self.current_phase == "NS" and ew_count > ns_count * 2 and ew_count > 3:
            return True
        if self.current_phase == "EW" and ns_count > ew_count * 2 and ns_count > 3:
            return True

        return False

    def get_light_state(self, direction: Direction) -> LightState:
        if direction in [Direction.NORTH, Direction.SOUTH]:
            return self.ns_state
        else:
            return self.ew_state

    def get_phase_time_remaining(self) -> float:
        elapsed = (datetime.now() - self.phase_start_time).total_seconds() * 1000
        current_state = self.ns_state if self.current_phase == "NS" else self.ew_state

        if current_state == LightState.GREEN:
            return max(0, self.green_duration - elapsed)
        elif current_state == LightState.YELLOW:
            return max(0, self.yellow_duration - elapsed)
        return 0

class CarManager:
    CAR_COLORS = [
        (59, 130, 246),
        (239, 68, 68),
        (16, 185, 129),
        (245, 158, 11),
        (139, 92, 246),
        (236, 72, 153)
    ]

    def __init__(self):
        self.cars: List[Car] = []
        self.next_id = 0
        self.stop_line_position = 350
        self.intersection_end = 450
        self.max_speed = 2.5
        self.min_distance = 40

    def spawn_car(self, direction: Direction) -> None:
        car = Car(
            id=f"car-{self.next_id}",
            direction=direction,
            position=0.0,
            speed=self.max_speed,
            committed=False,
            color=random.choice(self.CAR_COLORS)
        )
        self.next_id += 1
        self.cars.append(car)

    def update_cars(self, get_light_state, delta_time: float) -> None:
        cars_by_direction = self._group_cars_by_direction()

        for car in self.cars:
            light_state = get_light_state(car.direction)

            cars_ahead = [
                c for c in cars_by_direction[car.direction]
                if c.position > car.position and c.position - car.position < 100
            ]
            cars_ahead.sort(key=lambda c: c.position)
            nearest_car_ahead = cars_ahead[0] if cars_ahead else None

            if car.position >= self.intersection_end:
                car.committed = True
            elif car.position >= self.stop_line_position and not car.committed:
                if light_state == LightState.GREEN:
                    car.committed = True

            target_speed = self.max_speed

            if nearest_car_ahead:
                distance = nearest_car_ahead.position - car.position
                if distance < self.min_distance:
                    target_speed = 0
                elif distance < self.min_distance * 2:
                    target_speed = self.max_speed * 0.5

            if not car.committed and car.position < self.stop_line_position:
                if light_state in [LightState.RED, LightState.YELLOW]:
                    distance_to_stop = self.stop_line_position - car.position
                    if distance_to_stop < 50:
                        target_speed = min(target_speed, distance_to_stop / 20)

            car.speed += (target_speed - car.speed) * 0.1
            car.position += car.speed * delta_time

        self.cars = [car for car in self.cars if car.position < 800]

    def _group_cars_by_direction(self) -> Dict[Direction, List[Car]]:
        return {
            Direction.NORTH: [c for c in self.cars if c.direction == Direction.NORTH],
            Direction.SOUTH: [c for c in self.cars if c.direction == Direction.SOUTH],
            Direction.EAST: [c for c in self.cars if c.direction == Direction.EAST],
            Direction.WEST: [c for c in self.cars if c.direction == Direction.WEST]
        }

    def get_queue_count(self, direction: Direction) -> int:
        return len([
            c for c in self.cars
            if c.direction == direction
            and c.position < self.stop_line_position
            and not c.committed
        ])

    def get_cars(self) -> List[Car]:
        return self.cars

    def clear_cars(self) -> None:
        self.cars = []

class TrafficSimulation:
    def __init__(self, width: int = 1200, height: int = 900):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Traffic Intersection Simulation")

        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 28)
        self.font_medium = pygame.font.Font(None, 20)
        self.font_small = pygame.font.Font(None, 16)

        self.traffic_controller = TrafficController()
        self.car_manager = CarManager()

        self.spawn_rate = 2.0
        self.last_spawn_time = {
            Direction.NORTH: 0,
            Direction.SOUTH: 0,
            Direction.EAST: 0,
            Direction.WEST: 0
        }
        self.current_time = 0

        self.running = True

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.spawn_rate = min(5, self.spawn_rate + 0.5)
                elif event.key == pygame.K_DOWN:
                    self.spawn_rate = max(0.5, self.spawn_rate - 0.5)
                elif event.key == pygame.K_r:
                    self.reset()

    def reset(self) -> None:
        self.traffic_controller = TrafficController()
        self.car_manager = CarManager()
        self.last_spawn_time = {d: 0 for d in Direction}
        self.current_time = 0

    def update(self, delta_time: float) -> None:
        self.current_time += delta_time

        for direction in Direction:
            if self.current_time - self.last_spawn_time[direction] > self.spawn_rate * 1000 + random.random() * 1000:
                self.car_manager.spawn_car(direction)
                self.last_spawn_time[direction] = self.current_time

        queue_stats = {
            direction: self.car_manager.get_queue_count(direction)
            for direction in Direction
        }

        self.traffic_controller.update(queue_stats)
        self.car_manager.update_cars(
            lambda d: self.traffic_controller.get_light_state(d),
            delta_time
        )

    def draw_traffic_light(self, x: int, y: int, state: LightState) -> None:
        pygame.draw.rect(self.screen, (50, 50, 50), (x, y, 24, 90))

        red_color = (255, 0, 0) if state == LightState.RED else (139, 0, 0)
        yellow_color = (255, 255, 0) if state == LightState.YELLOW else (139, 139, 0)
        green_color = (0, 255, 0) if state == LightState.GREEN else (0, 139, 0)

        pygame.draw.circle(self.screen, red_color, (x + 12, y + 12), 6)
        pygame.draw.circle(self.screen, yellow_color, (x + 12, y + 42), 6)
        pygame.draw.circle(self.screen, green_color, (x + 12, y + 72), 6)

    def draw_car(self, car: Car, center_x: int, center_y: int) -> None:
        if car.direction == Direction.NORTH:
            x = center_x + 25
            y = center_y + 100 - car.position
            width, height = 20, 30
        elif car.direction == Direction.SOUTH:
            x = center_x - 25
            y = center_y - 100 + car.position
            width, height = 20, 30
        elif car.direction == Direction.EAST:
            x = center_x - 100 + car.position
            y = center_y - 25
            width, height = 30, 20
        else:
            x = center_x + 100 - car.position
            y = center_y + 25
            width, height = 30, 20

        pygame.draw.rect(self.screen, car.color, (x - width // 2, y - height // 2, width, height), border_radius=2)

    def draw_intersection(self) -> None:
        center_x, center_y = self.width // 2 - 200, self.height // 2
        intersection_size = 800

        pygame.draw.rect(self.screen, (100, 100, 100), (center_x, center_y, intersection_size, intersection_size))

        pygame.draw.rect(self.screen, (80, 80, 80), (center_x + 350, center_y, 100, 800))
        pygame.draw.rect(self.screen, (80, 80, 80), (center_x, center_y + 350, 800, 100))

        pygame.draw.rect(self.screen, (255, 255, 0), (center_x + 395, center_y, 10, 340))
        pygame.draw.rect(self.screen, (255, 255, 0), (center_x + 395, center_y + 460, 10, 340))
        pygame.draw.rect(self.screen, (255, 255, 0), (center_x, center_y + 395, 340, 10))
        pygame.draw.rect(self.screen, (255, 255, 0), (center_x + 460, center_y + 395, 340, 10))

        pygame.draw.rect(self.screen, (255, 255, 255), (center_x + 350, center_y + 348, 100, 4))
        pygame.draw.rect(self.screen, (255, 255, 255), (center_x + 350, center_y + 448, 100, 4))
        pygame.draw.rect(self.screen, (255, 255, 255), (center_x + 348, center_y + 350, 4, 100))
        pygame.draw.rect(self.screen, (255, 255, 255), (center_x + 448, center_y + 350, 4, 100))

        self.draw_traffic_light(center_x + 465, center_y + 320, self.traffic_controller.get_light_state(Direction.NORTH))
        self.draw_traffic_light(center_x + 310, center_y + 480, self.traffic_controller.get_light_state(Direction.SOUTH))
        self.draw_traffic_light(center_x + 480, center_y + 465, self.traffic_controller.get_light_state(Direction.EAST))
        self.draw_traffic_light(center_x + 320, center_y + 310, self.traffic_controller.get_light_state(Direction.WEST))

        for car in self.car_manager.get_cars():
            self.draw_car(car, center_x, center_y)

        text_n = self.font_large.render("N", True, (255, 255, 255))
        text_s = self.font_large.render("S", True, (255, 255, 255))
        text_e = self.font_large.render("E", True, (255, 255, 255))
        text_w = self.font_large.render("W", True, (255, 255, 255))

        self.screen.blit(text_n, (center_x + 385, center_y + 10))
        self.screen.blit(text_s, (center_x + 385, center_y + 770))
        self.screen.blit(text_e, (center_x + 770, center_y + 385))
        self.screen.blit(text_w, (center_x + 10, center_y + 385))

    def draw_control_panel(self) -> None:
        panel_width = 300
        pygame.draw.rect(self.screen, (255, 255, 255), (10, 10, panel_width, 400), border_radius=8)
        pygame.draw.rect(self.screen, (200, 200, 200), (10, 10, panel_width, 400), 2, border_radius=8)

        y_offset = 20
        title = self.font_large.render("Traffic Control", True, (30, 30, 30))
        self.screen.blit(title, (20, y_offset))
        y_offset += 40

        spawn_label = self.font_medium.render("Spawn Rate:", True, (50, 50, 50))
        self.screen.blit(spawn_label, (20, y_offset))
        spawn_value = self.font_medium.render(f"{self.spawn_rate:.1f}s", True, (0, 100, 200))
        self.screen.blit(spawn_value, (220, y_offset))
        y_offset += 35

        controls_text = self.font_small.render("UP/DOWN: Adjust spawn rate", True, (100, 100, 100))
        self.screen.blit(controls_text, (20, y_offset))
        y_offset += 25

        controls_text2 = self.font_small.render("R: Reset simulation", True, (100, 100, 100))
        self.screen.blit(controls_text2, (20, y_offset))
        y_offset += 40

        queue_title = self.font_medium.render("Queue Status:", True, (50, 50, 50))
        self.screen.blit(queue_title, (20, y_offset))
        y_offset += 30

        for direction in Direction:
            count = self.car_manager.get_queue_count(direction)
            queue_text = self.font_small.render(f"{direction.value.capitalize()}: {count}", True, (50, 50, 50))
            self.screen.blit(queue_text, (30, y_offset))
            y_offset += 25

        y_offset += 10
        phase_text = self.font_medium.render("Phase Time:", True, (50, 50, 50))
        self.screen.blit(phase_text, (20, y_offset))
        y_offset += 30

        time_remaining = self.traffic_controller.get_phase_time_remaining() / 1000
        time_text = self.font_large.render(f"{time_remaining:.1f}s", True, (0, 150, 200))
        self.screen.blit(time_text, (20, y_offset))

    def draw(self) -> None:
        self.screen.fill((40, 40, 40))
        self.draw_intersection()
        self.draw_control_panel()
        pygame.display.flip()

    def run(self) -> None:
        while self.running:
            self.handle_events()

            delta_time = self.clock.tick(60) / 1000.0 * 1000
            self.update(delta_time)
            self.draw()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    sim = TrafficSimulation()
    sim.run()
