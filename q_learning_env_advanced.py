# q_learning_env_advanced.py
#
# Environment for training a Q-learning agent.
# It simulates traffic flows in a 4-way intersection and
# lets the agent decide whether to keep the current phase (NS/EW) or switch.

import random
from enum import Enum


class Phase(Enum):
    # Two possible phases:
    # NS_GREEN: north/south are green, east/west are red
    # EW_GREEN: east/west are green, north/south are red
    NS_GREEN = 0
    EW_GREEN = 1


def discretize_queue(length: int) -> int:
    """
    Buckets queue length into 3 levels:
    0 = short queue (0–2 cars)
    1 = medium queue (3–5 cars)
    2 = long queue (6+ cars)
    """
    if length <= 2:
        return 0
    elif length <= 5:
        return 1
    else:
        return 2


def discretize_green_steps(steps: int) -> int:
    """
    Buckets how long the current phase has been green:
    0 = just turned green (very recent)
    1 = medium duration
    2 = green for a long time
    """
    if steps <= 3:
        return 0
    elif steps <= 8:
        return 1
    else:
        return 2


def discretize_diff(diff: int) -> int:
    """
    Discretizes the difference in total queues between EW and NS:
        diff = (EW_total - NS_total)

    Returns:
    -1 = NS has clearly more traffic
     0 = similar traffic on both axes
     1 = EW has clearly more traffic
    """
    if diff <= -3:
        return -1
    elif diff >= 3:
        return 1
    else:
        return 0


class TrafficEnvAdvanced:
    """
    Advanced traffic environment for Q-learning.

    - Simulates arrivals on N, S, E, W.
    - Controls the current phase: NS green or EW green.
    - Tracks how long the current phase has been active (green_steps).
    - Also collects simple metrics per episode (for analysis).
    """

    def __init__(
        self,
        base_arrival_prob: float = 0.3,
        capacity_per_step: int = 2,
        switch_penalty: float = 2.0,   # used as a base penalty for switching
    ):
        # Base probability of new cars arriving per step (per direction)
        self.base_arrival_prob = base_arrival_prob

        # How many cars can pass per step in the green directions
        self.capacity_per_step = capacity_per_step

        # Base penalty when switching phase (to avoid too many switches)
        self.switch_penalty = switch_penalty

        # Metrics per episode
        self.total_queue_sum = 0      # sum of total queues over all steps
        self.total_steps = 0          # number of steps in the current episode
        self.switches_this_episode = 0  # how many times we switched phase

        self.reset()

    def reset(self):
        """Resets the environment to the initial state and metrics, and returns the first state."""
        # Queues for each direction
        self.qN = 0
        self.qS = 0
        self.qE = 0
        self.qW = 0

        # Start with NS green by default
        self.phase = Phase.NS_GREEN

        # Number of steps since last phase change
        self.green_steps = 0

        # Reset episode metrics
        self.total_queue_sum = 0
        self.total_steps = 0
        self.switches_this_episode = 0

        return self._get_state()

    def _get_state(self):
        """
        Builds the discrete state representation used by Q-learning.

        The state is a tuple:
        (qN_bucket, qS_bucket, qE_bucket, qW_bucket,
         phase_val, green_bucket, diff_bucket)
        """
        qN_d = discretize_queue(self.qN)
        qS_d = discretize_queue(self.qS)
        qE_d = discretize_queue(self.qE)
        qW_d = discretize_queue(self.qW)

        # Total cars per axis
        ns_total = self.qN + self.qS
        ew_total = self.qE + self.qW

        # Difference in load between axes
        diff = ew_total - ns_total
        diff_bucket = discretize_diff(diff)

        # How long current phase has been green (bucketed)
        green_bucket = discretize_green_steps(self.green_steps)

        # Encode phase as 0 or 1
        phase_val = 0 if self.phase == Phase.NS_GREEN else 1

        return (qN_d, qS_d, qE_d, qW_d, phase_val, green_bucket, diff_bucket)

    def _arrivals(self):
        """
        Simulates new car arrivals in each direction.

        For each of N, S, E, W:
        - Slightly randomizes the arrival probability around base_arrival_prob.
        - Adds 1 car with that probability.
        """
        for attr in ["qN", "qS", "qE", "qW"]:
            # Add some noise to the base probability (but keep it reasonable)
            prob = self.base_arrival_prob + random.uniform(-0.05, 0.05)
            prob = max(0.05, min(0.6, prob))  # clamp between 0.05 and 0.6

            if random.random() < prob:
                setattr(self, attr, getattr(self, attr) + 1)

    def _departures(self):
        """
        Simulates how many cars leave the queues, depending on the current phase.
        Only directions with green light can have cars depart.
        """
        if self.phase == Phase.NS_GREEN:
            self.qN = max(0, self.qN - self.capacity_per_step)
            self.qS = max(0, self.qS - self.capacity_per_step)
        else:
            self.qE = max(0, self.qE - self.capacity_per_step)
            self.qW = max(0, self.qW - self.capacity_per_step)

    def step(self, action: int):
        """
        Performs one simulation step using the given action.

        action:
          0 = keep current phase (stay NS or stay EW)
          1 = switch phase (NS <-> EW)
        """
        # Total cars before action
        prev_total = self.qN + self.qS + self.qE + self.qW

        if action == 1:
            # Switch phase and reset green duration
            self.phase = Phase.EW_GREEN if self.phase == Phase.NS_GREEN else Phase.NS_GREEN
            self.green_steps = 0
            # Count this switch for metrics
            self.switches_this_episode += 1
        else:
            # Keep current phase and increase green duration
            self.green_steps += 1

        # Simulate traffic for this step
        self._arrivals()
        self._departures()

        # Total cars after updates
        new_total = self.qN + self.qS + self.qE + self.qW

        # ---- Update metrics ----
        self.total_queue_sum += new_total
        self.total_steps += 1
        # ------------------------

        # Reward design:
        # + Strong reward for reducing queues
        # - Mild penalty for having cars waiting
        # - Moderate penalty for switching phase
        # - Strong penalty for extreme congestion

        reduction = prev_total - new_total

        # Encourage quick reduction of queues
        reward = 1.0 * reduction

        # Mild penalty for having cars in the system
        reward -= 0.3 * new_total

        # Penalize switching (but not too much)
        if action == 1:
            reward -= self.switch_penalty

        # Extra penalties for very high congestion
        if new_total > 12:
            reward -= 5
        if new_total > 20:
            reward -= 10

        next_state = self._get_state()
        return next_state, reward
