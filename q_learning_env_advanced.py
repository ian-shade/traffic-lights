# q_learning_env_advanced.py
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

def discretize_green_steps(steps: int) -> int:
    """
    0 = verde reciente, 1 = medio, 2 = verde muy largo
    """
    if steps <= 3:
        return 0
    elif steps <= 8:
        return 1
    else:
        return 2

def discretize_diff(diff: int) -> int:
    """
    diff = (EW - NS)
    -1 = NS tiene más tráfico
     0 = similar
     1 = EW tiene más tráfico
    """
    if diff <= -3:
        return -1
    elif diff >= 3:
        return 1
    else:
        return 0

class TrafficEnvAdvanced:
    """
    Entorno avanzado para entrenar Q-learning.
    - Simula llegadas en N, S, E, W
    - Controla fase NS/EW
    - Lleva cuenta de cuánto tiempo lleva la fase actual
    """

    def __init__(
        self,
        base_arrival_prob: float = 0.3,
        capacity_per_step: int = 2,
        switch_penalty: float = 3.0
    ):
        self.base_arrival_prob = base_arrival_prob
        self.capacity_per_step = capacity_per_step
        self.switch_penalty = switch_penalty
        self.reset()

    def reset(self):
        # colas
        self.qN = 0
        self.qS = 0
        self.qE = 0
        self.qW = 0

        # empezamos con NS en verde
        self.phase = Phase.NS_GREEN
        # pasos desde el último cambio de fase
        self.green_steps = 0

        return self._get_state()

    def _get_state(self):
        qN_d = discretize_queue(self.qN)
        qS_d = discretize_queue(self.qS)
        qE_d = discretize_queue(self.qE)
        qW_d = discretize_queue(self.qW)

        ns_total = self.qN + self.qS
        ew_total = self.qE + self.qW
        diff = ew_total - ns_total
        diff_bucket = discretize_diff(diff)

        green_bucket = discretize_green_steps(self.green_steps)
        phase_val = 0 if self.phase == Phase.NS_GREEN else 1

        return (qN_d, qS_d, qE_d, qW_d, phase_val, green_bucket, diff_bucket)

    def _arrivals(self):
        """
        Simula llegadas. Podrías hacerlo más fancy (hora pico en un eje),
        pero así ya da bastante juego.
        """
        # pequeño ruido aleatorio en cada dirección
        for attr in ["qN", "qS", "qE", "qW"]:
            prob = self.base_arrival_prob + random.uniform(-0.1, 0.1)
            prob = max(0.05, min(0.7, prob))
            if random.random() < prob:
                setattr(self, attr, getattr(self, attr) + 1)

    def _departures(self):
        """
        Coches que pasan en la fase actual.
        """
        if self.phase == Phase.NS_GREEN:
            self.qN = max(0, self.qN - self.capacity_per_step)
            self.qS = max(0, self.qS - self.capacity_per_step)
        else:
            self.qE = max(0, self.qE - self.capacity_per_step)
            self.qW = max(0, self.qW - self.capacity_per_step)

    def step(self, action: int):
        """
        action:
          0 = mantener fase
          1 = cambiar fase NS <-> EW
        """
        prev_total = self.qN + self.qS + self.qE + self.qW

        if action == 1:
            # cambiamos de fase
            self.phase = Phase.EW_GREEN if self.phase == Phase.NS_GREEN else Phase.NS_GREEN
            self.green_steps = 0
        else:
            # mantenemos fase, aumenta duración del verde
            self.green_steps += 1

        # Simular tráfico
        self._arrivals()
        self._departures()

        new_total = self.qN + self.qS + self.qE + self.qW

        # Recompensa:
        # + reducción en colas
        # - penalización por colas grandes
        # - penalización por cambiar de fase
        reduction = prev_total - new_total
        reward = 0.5 * reduction - 0.5 * new_total
        if action == 1:
            reward -= self.switch_penalty

        next_state = self._get_state()
        return next_state, reward
