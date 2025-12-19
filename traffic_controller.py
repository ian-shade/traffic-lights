# traffic_controller.py
from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional, Any

from models import Direction, LightState


class TrafficController:
    """Intersection signal logic with:
    - realistic phase timing (min green, yellow)
    - VIP preemption
    - pluggable decision controller for *early* switching (rule-based / max-pressure / fuzzy / RL)
    """

    def __init__(self):
        # Current active axis ("NS" or "EW")
        self.current_phase = "NS"
        self.phase_start_time = datetime.now()

        # Light durations (ms)
        self.green_duration = 30000         # nominal green if no early-switch
        self.yellow_duration = 3000
        self.min_green_duration = 10000     # minimum time before switching early

        # Current light states
        self.ns_state = LightState.GREEN
        self.ew_state = LightState.RED

        # Optional external controller (must implement act(...) -> 0/1)
        self.decision_controller: Optional[Any] = None

    # --- Public API ---------------------------------------------------------
    def set_controller(self, controller: Optional[Any]) -> None:
        """Attach a controller (or None to disable)."""
        self.decision_controller = controller

        # If the controller has reset, call it (safe)
        if controller is not None and hasattr(controller, "reset"):
            try:
                controller.reset()
            except Exception:
                pass

    # Backwards compatible name
    def set_q_controller(self, q_controller: Optional[Any]) -> None:
        self.set_controller(q_controller)

    def get_light_state(self, direction: Direction) -> LightState:
        if direction in (Direction.NORTH, Direction.SOUTH):
            return self.ns_state
        return self.ew_state

    def update(self, queue_stats: Dict[Direction, int], vip_queue_stats: Dict[Direction, int]) -> None:
        """Update lights based on timing, VIP preemption, and optional controller."""

        # VIP totals per axis
        ns_vips = vip_queue_stats[Direction.NORTH] + vip_queue_stats[Direction.SOUTH]
        ew_vips = vip_queue_stats[Direction.EAST] + vip_queue_stats[Direction.WEST]

        # If any VIPs are waiting, give them priority immediately
        if ns_vips > 0 or ew_vips > 0:
            self._handle_vip_preemption(ns_vips, ew_vips)
            return

        elapsed = (datetime.now() - self.phase_start_time).total_seconds() * 1000.0

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

        else:  # EW phase
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

    # --- Internal decision logic -------------------------------------------
    def _should_switch_phase(self, queue_stats: Dict[Direction, int], elapsed_ms: float) -> bool:
        """Ask the controller (or fallback heuristic) whether to switch early."""

        # Enforce minimum green (prevents flicker)
        if elapsed_ms < self.min_green_duration:
            return False

        ns_count = queue_stats[Direction.NORTH] + queue_stats[Direction.SOUTH]
        ew_count = queue_stats[Direction.EAST] + queue_stats[Direction.WEST]

        # If nobody is waiting anywhere, never switch early
        if (ns_count + ew_count) == 0:
            return False

        # External controller decision
        if self.decision_controller is not None:
            green_elapsed_s = int(elapsed_ms / 1000.0)
            phase_val = 0 if self.current_phase == "NS" else 1
            try:
                action = self.decision_controller.act(
                    queue_stats[Direction.NORTH],
                    queue_stats[Direction.SOUTH],
                    queue_stats[Direction.EAST],
                    queue_stats[Direction.WEST],
                    phase_val,
                    green_elapsed_s,
                )
                return bool(action == 1)
            except Exception:
                # If controller fails, fall back to simple imbalance heuristic
                pass

        # Fallback: switch if other axis has 2x more cars and current axis isn't empty
        if self.current_phase == "NS":
            return ew_count > max(3, 2 * ns_count)
        else:
            return ns_count > max(3, 2 * ew_count)

    def _handle_vip_preemption(self, ns_vips: int, ew_vips: int) -> None:
        """VIP logic: whichever axis has VIP cars waiting gets immediate green."""
        if ns_vips > 0 and ew_vips == 0:
            desired_phase = "NS"
        elif ew_vips > 0 and ns_vips == 0:
            desired_phase = "EW"
        else:
            desired_phase = self.current_phase

        self._set_phase_immediately(desired_phase)

    def _set_phase_immediately(self, phase: str) -> None:
        if phase == "NS":
            self.current_phase = "NS"
            self.ns_state = LightState.GREEN
            self.ew_state = LightState.RED
        else:
            self.current_phase = "EW"
            self.ns_state = LightState.RED
            self.ew_state = LightState.GREEN

        self.phase_start_time = datetime.now()

    def get_phase_time_remaining(self) -> float:
        """
        Devuelve el tiempo restante (ms) de la fase actual (GREEN/YELLOW).
        Si estás en RED, regresa 0.
        """
        from datetime import datetime
        from models import LightState
    
        elapsed = (datetime.now() - self.phase_start_time).total_seconds() * 1000.0

        # Estado actual según la fase activa
        current_state = self.ns_state if self.current_phase == "NS" else self.ew_state

        if current_state == LightState.GREEN:
            return max(0.0, float(self.green_duration) - elapsed)
        elif current_state == LightState.YELLOW:
            return max(0.0, float(self.yellow_duration) - elapsed)
    
        return 0.0

