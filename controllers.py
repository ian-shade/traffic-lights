# controllers.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple, Dict, Any
import json
from ast import literal_eval

# NOTE: All controllers expose:
#   - reset()
#   - act(qN, qS, qE, qW, phase_val, green_elapsed_s) -> int
# where:
#   phase_val: 0 = NS is green, 1 = EW is green
#   return: 0 = keep current phase, 1 = switch phase


@dataclass
class ActuatedThresholdParams:
    # If the opposing axis queue is this much larger than the current axis, request a switch
    imbalance_switch: int = 6
    # If current axis is basically empty, allow early switch
    current_empty_threshold: int = 1
    # If opposing axis has at least this many cars, and current is small, switch
    opposing_min_to_switch: int = 3
    # Optional "max green" request for safety (TrafficController also has its own)
    max_green_s: int = 60


class ActuatedThresholdController:
    """Rule-based actuated logic using queue thresholds + imbalance.
    Great 'explainable' baseline (KBS-style rules).
    """

    def __init__(self, params: Optional[ActuatedThresholdParams] = None):
        self.p = params or ActuatedThresholdParams()

    def reset(self) -> None:
        pass

    def act(self, qN: int, qS: int, qE: int, qW: int, phase_val: int, green_elapsed_s: int) -> int:
        ns = qN + qS
        ew = qE + qW

        # Safety cap
        if green_elapsed_s >= self.p.max_green_s:
            return 1

        if phase_val == 0:  # NS is green
            current = ns
            other = ew
        else:               # EW is green
            current = ew
            other = ns

        # If nobody is waiting anywhere, keep
        if (ns + ew) == 0:
            return 0

        # Rule 1: if current axis is empty-ish and other has cars, switch
        if current <= self.p.current_empty_threshold and other >= self.p.opposing_min_to_switch:
            return 1

        # Rule 2: if other axis is significantly larger, switch
        if (other - current) >= self.p.imbalance_switch:
            return 1

        return 0


@dataclass
class MaxPressureParams:
    # Hysteresis prevents flicker: require the new phase to beat the current by margin
    hysteresis_margin: int = 2
    # Optional cap
    max_green_s: int = 60


class MaxPressureController:
    """Max-Pressure style controller (simplified, 2-phase).
    Pressure for NS is (NS queue - EW queue); for EW it's the opposite.
    Switch if opposing pressure exceeds current by hysteresis.
    """

    def __init__(self, params: Optional[MaxPressureParams] = None):
        self.p = params or MaxPressureParams()

    def reset(self) -> None:
        pass

    def act(self, qN: int, qS: int, qE: int, qW: int, phase_val: int, green_elapsed_s: int) -> int:
        ns = qN + qS
        ew = qE + qW

        if green_elapsed_s >= self.p.max_green_s:
            return 1

        # If nobody is waiting, keep
        if (ns + ew) == 0:
            return 0

        # Pressure difference: positive means NS is more 'urgent'
        diff = ns - ew

        # If NS green, switch only if EW is significantly more urgent (diff << 0)
        if phase_val == 0:
            return 1 if (-diff) >= self.p.hysteresis_margin else 0
        # If EW green, switch only if NS is significantly more urgent (diff >> 0)
        return 1 if diff >= self.p.hysteresis_margin else 0


class QTableController:
    """Loads a trained Q-table (q_table_advanced.json) and chooses actions:
        0 = keep current phase
        1 = switch phase
    """

    def __init__(self, q_table_path: str = "q_table_advanced.json"):
        with open(q_table_path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        # keys are strings like "(0, 1, 0, 2, 0, 1, -1)"
        self.Q: Dict[Tuple[Any, ...], list] = {literal_eval(k): v for k, v in raw.items()}

    def reset(self) -> None:
        pass

    # --- Discretizers must match training (train_q_learning_advanced.py) ---
    def _discretize_queue(self, q: int) -> int:
        # MUST match q_learning_env_advanced.py: 0-2->0, 3-5->1, 6+->2
        if q <= 2:
            return 0
        elif q <= 5:
            return 1
        else:
            return 2

    def _discretize_green_steps(self, green_steps: int) -> int:
        # Your sim passes seconds; training used "steps", but thresholds are same.
        # Keeping the same buckets as training:
        if green_steps <= 3:
            return 0
        elif green_steps <= 8:
            return 1
        else:
            return 2

    def _discretize_diff(self, diff: int) -> int:
        # MUST match q_learning_env_advanced.py (EW_total - NS_total):
        if diff <= -3:
            return -1
        elif diff >= 3:
            return 1
        else:
            return 0


    def act(self, qN: int, qS: int, qE: int, qW: int, phase_val: int, green_elapsed_s: float) -> int:
        ns = qN + qS
        ew = qE + qW
        diff_bucket = self._discretize_diff(ew - ns)

        green_steps_like_training = int(green_elapsed_s)

        state = (
            self._discretize_queue(qN),
            self._discretize_queue(qS),
            self._discretize_queue(qE),
            self._discretize_queue(qW),
            int(phase_val),
            self._discretize_green_steps(green_steps_like_training),
            diff_bucket,
        )

        q_values = self.Q.get(state, [0.0, 0.0])
        return 0 if q_values[0] >= q_values[1] else 1
