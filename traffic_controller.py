# traffic_controller.py
from datetime import datetime
from typing import Dict

from models import Direction, LightState


class TrafficController:
    def __init__(self):
        # Current active direction (NS or EW)
        self.current_phase = "NS"

        # Timer for the current phase
        self.phase_start_time = datetime.now()

        # Light durations (in ms)
        self.green_duration = 30000
        self.yellow_duration = 3000
        self.min_green_duration = 10000  # minimum time before switching

        # Initial light states
        self.ns_state = LightState.GREEN
        self.ew_state = LightState.RED

    def update(
        self,
        queue_stats: Dict[Direction, int],
        vip_queue_stats: Dict[Direction, int]
    ) -> None:
        """
        Handles the decision of switching lights.
        VIP cars take priority and can force an immediate green.
        """

        # Count VIPs per axis
        ns_vips = vip_queue_stats[Direction.NORTH] + vip_queue_stats[Direction.SOUTH]
        ew_vips = vip_queue_stats[Direction.EAST] + vip_queue_stats[Direction.WEST]

        # If any VIPs are waiting, give them priority
        if ns_vips > 0 or ew_vips > 0:
            self._handle_vip_preemption(ns_vips, ew_vips)
            return

        # Normal timing logic (no VIP present)
        elapsed = (datetime.now() - self.phase_start_time).total_seconds() * 1000

        if self.current_phase == "NS":
            # NS is currently green/yellow
            if self.ns_state == LightState.GREEN:
                should_switch = self._should_switch_phase(queue_stats, elapsed)
                if elapsed >= self.green_duration or should_switch:
                    # Switch to yellow
                    self.ns_state = LightState.YELLOW
                    self.phase_start_time = datetime.now()

            elif self.ns_state == LightState.YELLOW:
                # After yellow, switch to EW-green
                if elapsed >= self.yellow_duration:
                    self.ns_state = LightState.RED
                    self.ew_state = LightState.GREEN
                    self.current_phase = "EW"
                    self.phase_start_time = datetime.now()

        else:
            # EW is currently green/yellow
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
        """
        Decides whether to switch early based on queue imbalance.
        Prevents switching too early by enforcing a minimum green time.
        """

        if elapsed < self.min_green_duration:
            return False

        # Total cars waiting on each axis
        ns_count = queue_stats[Direction.NORTH] + queue_stats[Direction.SOUTH]
        ew_count = queue_stats[Direction.EAST] + queue_stats[Direction.WEST]

        # If one side is very crowded, switch earlier
        if self.current_phase == "NS" and ew_count > ns_count * 2 and ew_count > 3:
            return True
        if self.current_phase == "EW" and ns_count > ew_count * 2 and ns_count > 3:
            return True

        return False

    def _handle_vip_preemption(self, ns_vips: int, ew_vips: int) -> None:
        """
        VIP logic: whichever axis has VIP cars waiting gets immediate green.
        """

        if ns_vips > 0 and ew_vips == 0:
            desired_phase = "NS"
        elif ew_vips > 0 and ns_vips == 0:
            desired_phase = "EW"
        else:
            # If both have VIPs, keep the current phase ( simplest rule )
            desired_phase = self.current_phase

        self._set_phase_immediately(desired_phase)

    def _set_phase_immediately(self, phase: str) -> None:
        """Instantly switches lights to give priority to VIP cars."""
        self.current_phase = phase
        self.phase_start_time = datetime.now()

        if phase == "NS":
            self.ns_state = LightState.GREEN
            self.ew_state = LightState.RED
        else:  # EW phase
            self.ns_state = LightState.RED
            self.ew_state = LightState.GREEN

    def get_light_state(self, direction: Direction) -> LightState:
        """Returns the current light state for a given lane direction."""
        if direction in [Direction.NORTH, Direction.SOUTH]:
            return self.ns_state
        else:
            return self.ew_state

    def get_phase_time_remaining(self) -> float:
        """Returns how much time is left in the current phase."""
        elapsed = (datetime.now() - self.phase_start_time).total_seconds() * 1000
        current_state = self.ns_state if self.current_phase == "NS" else self.ew_state

        if current_state == LightState.GREEN:
            return max(0, self.green_duration - elapsed)
        elif current_state == LightState.YELLOW:
            return max(0, self.yellow_duration - elapsed)

        return 0
