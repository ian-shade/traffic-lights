# q_learning_env.py
import random
from enum import Enum

class Phase(Enum):
    NS_GREEN = 0
    EW_GREEN = 1

def discretize_queue(length: int) -> int:
    if length <= 2:
        return 0
    elif length <= 5:
        return 1
    else:
        return 2

class TrafficEnv:
    """
    Entorno abstracto, sin pygame.
    Simula colas con llegadas y salidas aleatorias.
    """

    def __init__(self, arrival_prob: float = 0.35, capacity_per_step: int = 2, switch_penalty: float = 2.0):
        self.arrival_prob = arrival_prob
        self.capacity_per_step = capacity_per_step
        self.switch_penalty = switch_penalty
        self.reset()

    def reset(self):
        self.qN = 0
        self.qS = 0
        self.qE = 0
        self.qW = 0
        self.phase = Phase.NS_GREEN
        return self._get_state()

    def _get_state(self):
        return (
            discretize_queue(self.qN),
            discretize_queue(self.qS),
            discretize_queue(self.qE),
            discretize_queue(self.qW),
            self.phase.value,
        )

    def _arrivals(self):
        for attr in ["qN", "qS", "qE", "qW"]:
            if random.random() < self.arrival_prob:
                setattr(self, attr, getattr(self, attr) + 1)

    def _departures(self):
        if self.phase == Phase.NS_GREEN:
            self.qN = max(0, self.qN - self.capacity_per_step)
            self.qS = max(0, self.qS - self.capacity_per_step)
        else:
            self.qE = max(0, self.qE - self.capacity_per_step)
            self.qW = max(0, self.qW - self.capacity_per_step)

    def step(self, action: int):
        """
        action 0 = mantener fase
        action 1 = cambiar de NS a EW o viceversa
        """
        if action == 1:
            self.phase = Phase.EW_GREEN if self.phase == Phase.NS_GREEN else Phase.NS_GREEN

        self._arrivals()
        self._departures()

        total_queue = self.qN + self.qS + self.qE + self.qW
        reward = -float(total_queue)
        if action == 1:
            reward -= self.switch_penalty

        next_state = self._get_state()
        return next_state, reward
