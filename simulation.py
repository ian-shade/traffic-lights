# simulation.py
import sys
import random
from typing import Dict

import pygame

from models import Direction, LightState, Car
from traffic_controller import TrafficController
from car_manager import CarManager


class TrafficSimulation:
    def __init__(self, width: int = 1200, height: int = 900):
        # Window size and game setup
        self.width = width
        self.height = height

        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Traffic Intersection Simulation")

        # Clock + fonts used for drawing text
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 28)
        self.font_medium = pygame.font.Font(None, 20)
        self.font_small = pygame.font.Font(None, 16)

        # Main controllers
        self.traffic_controller = TrafficController()  # manages traffic lights
        self.car_manager = CarManager()                # creates and moves cars

        # Car spawning settings
        self.spawn_rate = 2.0      # seconds between random spawns
        self.last_spawn_time = 0
        self.current_time = 0

        self.running = True

    def handle_events(self) -> None:
        """Handles keyboard and window events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                # Increase or decrease car spawn speed
                if event.key == pygame.K_UP:
                    self.spawn_rate = min(5, self.spawn_rate + 0.5)
                elif event.key == pygame.K_DOWN:
                    self.spawn_rate = max(0.5, self.spawn_rate - 0.5)

                # Reset everything
                elif event.key == pygame.K_r:
                    self.reset()

                # Optional: manually spawn VIP cars for testing
                elif event.key == pygame.K_1:
                    self.car_manager.spawn_car(Direction.NORTH, force_vip=True)
                elif event.key == pygame.K_2:
                    self.car_manager.spawn_car(Direction.SOUTH, force_vip=True)
                elif event.key == pygame.K_3:
                    self.car_manager.spawn_car(Direction.EAST, force_vip=True)
                elif event.key == pygame.K_4:
                    self.car_manager.spawn_car(Direction.WEST, force_vip=True)

    def reset(self) -> None:
        """Resets the simulation state."""
        self.traffic_controller = TrafficController()
        self.car_manager = CarManager()
        self.last_spawn_time = 0
        self.current_time = 0

    def draw_traffic_light(self, x: int, y: int, state: LightState, horizontal: bool = False) -> None:
        """Draws a single traffic light at the given position."""
        # Colors depend on active light
        red_color = (255, 0, 0) if state == LightState.RED else (139, 0, 0)
        yellow_color = (255, 255, 0) if state == LightState.YELLOW else (139, 139, 0)
        green_color = (0, 255, 0) if state == LightState.GREEN else (0, 139, 0)

        # Vertical light (for N/S)
        if not horizontal:
            pygame.draw.rect(self.screen, (50, 50, 50), (x, y, 24, 90))
            pygame.draw.circle(self.screen, red_color,    (x + 12, y + 12), 6)
            pygame.draw.circle(self.screen, yellow_color, (x + 12, y + 42), 6)
            pygame.draw.circle(self.screen, green_color,  (x + 12, y + 72), 6)

        # Horizontal light (for E/W)
        else:
            pygame.draw.rect(self.screen, (50, 50, 50), (x, y, 90, 24))
            pygame.draw.circle(self.screen, red_color,    (x + 12, y + 12), 6)
            pygame.draw.circle(self.screen, yellow_color, (x + 45, y + 12), 6)
            pygame.draw.circle(self.screen, green_color,  (x + 78, y + 12), 6)

    def draw_car(self, car: Car, center_x: int, center_y: int) -> None:
        """Draws a car depending on its direction and position."""
        intersection_size = 800
        s = car.position  # distance traveled along the lane

        # Convert lane direction into (x, y) positions
        if car.direction == Direction.NORTH:
            x = center_x + 425
            y = center_y + intersection_size - s
            width, height = 20, 30
        elif car.direction == Direction.SOUTH:
            x = center_x + 375
            y = center_y + s
            width, height = 20, 30
        elif car.direction == Direction.EAST:
            x = center_x + s
            y = center_y + 425
            width, height = 30, 20
        else:  # WEST
            x = center_x + intersection_size - s
            y = center_y + 375
            width, height = 30, 20

        # Draw the car body
        car_rect = pygame.Rect(x - width // 2, y - height // 2, width, height)
        pygame.draw.rect(self.screen, car.color, car_rect, border_radius=2)

        # VIP cars get a white border + siren
        if car.is_vip:
            pygame.draw.rect(self.screen, (255, 255, 255), car_rect, width=2, border_radius=2)
            pygame.draw.circle(self.screen, (0, 200, 255), (car_rect.centerx, car_rect.top), 4)

    def draw_intersection(self) -> None:
        """Draws streets, markings, traffic lights and all cars."""
        intersection_size = 800
        center_x = (self.width  - intersection_size) // 2
        center_y = (self.height - intersection_size) // 2

        # Road boundaries
        road_v_left = center_x + 350
        road_v_right = center_x + 450
        road_h_top = center_y + 350
        road_h_bottom = center_y + 450

        # Intersection base (simple grey background)
        pygame.draw.rect(self.screen, (100, 100, 100), (center_x, center_y, intersection_size, intersection_size))

        # Vertical and horizontal roads
        pygame.draw.rect(self.screen, (80, 80, 80), (center_x + 350, center_y, 100, 800))
        pygame.draw.rect(self.screen, (80, 80, 80), (center_x, center_y + 350, 800, 100))

        # Yellow lane dividers
        pygame.draw.rect(self.screen, (255, 255, 0), (center_x + 395, center_y, 10, 340))
        pygame.draw.rect(self.screen, (255, 255, 0), (center_x + 395, center_y + 460, 10, 340))
        pygame.draw.rect(self.screen, (255, 255, 0), (center_x, center_y + 395, 340, 10))
        pygame.draw.rect(self.screen, (255, 255, 0), (center_x + 460, center_y + 395, 340, 10))

        # White stop lines
        pygame.draw.rect(self.screen, (255, 255, 255), (center_x + 350, center_y + 348, 100, 4))
        pygame.draw.rect(self.screen, (255, 255, 255), (center_x + 350, center_y + 448, 100, 4))
        pygame.draw.rect(self.screen, (255, 255, 255), (center_x + 348, center_y + 350, 4, 100))
        pygame.draw.rect(self.screen, (255, 255, 255), (center_x + 448, center_y + 350, 4, 100))

        # Draw traffic lights in each direction
        self.draw_traffic_light( road_v_right + 10, road_h_bottom - 95,
                                 self.traffic_controller.get_light_state(Direction.EAST),
                                 horizontal=False )

        self.draw_traffic_light( road_v_left - 34, road_h_top + 5,
                                 self.traffic_controller.get_light_state(Direction.WEST),
                                 horizontal=False )

        self.draw_traffic_light( road_v_left + 5, road_h_bottom + 10,
                                 self.traffic_controller.get_light_state(Direction.NORTH),
                                 horizontal=True )

        self.draw_traffic_light( road_v_right - 95, road_h_top - 34,
                                 self.traffic_controller.get_light_state(Direction.SOUTH),
                                 horizontal=True )

        # Draw every car on screen
        for car in self.car_manager.get_cars():
            self.draw_car(car, center_x, center_y)

        # Compass labels (N/S/E/W)
        text_n = self.font_large.render("N", True, (255, 255, 255))
        text_s = self.font_large.render("S", True, (255, 255, 255))
        text_e = self.font_large.render("E", True, (255, 255, 255))
        text_w = self.font_large.render("W", True, (255, 255, 255))

        self.screen.blit(text_n, (center_x + 385, center_y + 10))
        self.screen.blit(text_s, (center_x + 385, center_y + 770))
        self.screen.blit(text_e, (center_x + 770, center_y + 385))
        self.screen.blit(text_w, (center_x + 10, center_y + 385))

    def draw_control_panel(self) -> None:
        """Displays spawn rate, queue counts and phase time."""
        panel_width = 300

        # Background box
        pygame.draw.rect(self.screen, (255, 255, 255), (10, 10, panel_width, 400), border_radius=8)
        pygame.draw.rect(self.screen, (200, 200, 200), (10, 10, panel_width, 400), 2, border_radius=8)

        y_offset = 20
        title = self.font_large.render("Traffic Control", True, (30, 30, 30))
        self.screen.blit(title, (20, y_offset))
        y_offset += 40

        # Spawn rate display
        spawn_label = self.font_medium.render("Spawn Rate:", True, (50, 50, 50))
        self.screen.blit(spawn_label, (20, y_offset))
        spawn_value = self.font_medium.render(f"{self.spawn_rate:.1f}s", True, (0, 100, 200))
        self.screen.blit(spawn_value, (220, y_offset))
        y_offset += 35

        self.screen.blit(self.font_small.render("UP/DOWN: Adjust spawn rate", True, (100, 100, 100)), (20, y_offset))
        y_offset += 25

        self.screen.blit(self.font_small.render("R: Reset simulation", True, (100, 100, 100)), (20, y_offset))
        y_offset += 40

        # Queue sizes
        queue_title = self.font_medium.render("Queue Status:", True, (50, 50, 50))
        self.screen.blit(queue_title, (20, y_offset))
        y_offset += 30

        # These names correspond to what the user sees on-screen
        counts: Dict[str, int] = {
            "North": self.car_manager.get_queue_count(Direction.SOUTH),
            "South": self.car_manager.get_queue_count(Direction.NORTH),
            "East":  self.car_manager.get_queue_count(Direction.WEST),
            "West":  self.car_manager.get_queue_count(Direction.EAST),
        }

        for name, count in counts.items():
            txt = self.font_small.render(f"{name}: {count}", True, (50, 50, 50))
            self.screen.blit(txt, (30, y_offset))
            y_offset += 25

        # Phase timer
        y_offset += 10
        self.screen.blit(self.font_medium.render("Phase Time:", True, (50, 50, 50)), (20, y_offset))
        y_offset += 30

        time_remaining = self.traffic_controller.get_phase_time_remaining() / 1000
        txt_time = self.font_large.render(f"{time_remaining:.1f}s", True, (0, 150, 200))
        self.screen.blit(txt_time, (20, y_offset))

    def update(self, delta_time: float) -> None:
        """Main update loop: spawns cars, updates lights, moves cars."""
        self.current_time += delta_time

        # Random spawn (with some randomness added)
        if self.current_time - self.last_spawn_time > self.spawn_rate * 1000 + random.random() * 1000:
            direction = random.choice(list(Direction))
            self.car_manager.spawn_car(direction)
            self.last_spawn_time = self.current_time

        # Collect queue sizes
        queue_stats = {d: self.car_manager.get_queue_count(d) for d in Direction}
        vip_queue_stats = {d: self.car_manager.get_vip_queue_count(d) for d in Direction}

        # Update traffic lights (VIPs have priority)
        self.traffic_controller.update(queue_stats, vip_queue_stats)

        # Move cars according to light rules
        self.car_manager.update_cars(
            lambda d: self.traffic_controller.get_light_state(d),
            delta_time
        )

    def draw(self) -> None:
        """Clears the screen and redraws everything."""
        self.screen.fill((40, 40, 40))
        self.draw_intersection()
        self.draw_control_panel()
        pygame.display.flip()

    def run(self) -> None:
        """Main game loop."""
        while self.running:
            self.handle_events()
            delta_time = self.clock.tick(60) / 1000.0 * 1000
            self.update(delta_time)
            self.draw()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    pygame.init()
    sim = TrafficSimulation()
    sim.run()
