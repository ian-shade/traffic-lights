from dataclasses import dataclass, field
import numpy as np
from typing import Dict, List, Tuple
from config import ArrivalCfg, SimCfg, LANE_OFF, ENTER, EXIT, STOP_LINE
from traffic_signal import FourSignalController, MultiSignalCfg

# Trayectorias rectas (solo carril de entrada)
def path_straight(d: str):
    if d == "N":  # de arriba hacia abajo (x = +LANE_OFF)
        return lambda s: (+LANE_OFF,  ENTER - s * (ENTER + EXIT))
    if d == "S":  # de abajo hacia arriba (x = -LANE_OFF)
        return lambda s: (-LANE_OFF, -ENTER + s * (ENTER + EXIT))
    if d == "E":  # de derecha a izquierda (y = -LANE_OFF)
        return lambda s: ( ENTER - s * (ENTER + EXIT), -LANE_OFF)
    if d == "W":  # de izquierda a derecha (y = +LANE_OFF)
        return lambda s: (-ENTER + s * (ENTER + EXIT), +LANE_OFF)
    raise ValueError(d)

@dataclass
class Car:
    d: str
    s: float = 0.0
    def pos(self) -> Tuple[float, float]:
        return path_straight(self.d)(self.s)

@dataclass
class IntersectionSim:
    arrivals: ArrivalCfg
    sim: SimCfg
    signal: FourSignalController
    rng: np.random.Generator = field(default_factory=lambda: np.random.default_rng(7))
    q: Dict[str, List[Car]] = field(default_factory=lambda: {k: [] for k in "NESW"})

    def spawn(self):
        lam = dict(N=self.arrivals.lam_N, E=self.arrivals.lam_E,
                   S=self.arrivals.lam_S, W=self.arrivals.lam_W)
        for d in "NESW":
            k = self.rng.poisson(lam[d])
            k = min(k, max(0, self.sim.max_queue - len(self.q[d])))
            for _ in range(k):
                self.q[d].append(Car(d))

    # con el controlador de 4 fases no necesitamos decidir nada aquí
    def decide(self):
        pass

    def step(self):
        self.spawn()
        self.decide()

        speed = self.sim.speed
        gap_s = self.sim.gap_s

        # Línea de alto donde quieres que paren (usando tu STOP_LINE=0.25)
        STOP_AT = STOP_LINE
        s_stop  = (ENTER - STOP_AT) / (ENTER + EXIT)
        s_eps   = 1e-3

        # Índices por tu numeración: 1=S→N, 2=E→W, 3=W→E, 4=N→S
        dir_idx = {"S": 0, "E": 1, "W": 2, "N": 3}

        for d in "NESW":
            arr = self.q[d]
            if not arr:
                continue

            green = self.signal.is_green(dir_idx[d])

            # líder
            lead = arr[0]
            if lead.s < s_stop - s_eps:
                # se aproxima aunque haya rojo (más lento)
                lead.s = min(s_stop, lead.s + speed * 0.6)
            else:
                if green:
                    lead.s = min(1.0, lead.s + speed)
                    if lead.s >= 1.0:
                        arr.pop(0)
                else:
                    # en rojo, clavado en la línea de alto
                    lead.s = min(lead.s, s_stop)

            # seguidores (nunca pasan la línea ni al coche de adelante)
            for i in range(1, len(arr)):
                car  = arr[i]
                prev = arr[i - 1]
                target = min(s_stop - s_eps, prev.s - gap_s)
                target = max(0.0, target)
                if car.s < target:
                    car.s = min(target, car.s + speed * 0.6)

        # avanzamos el controlador de semáforos al final del tick
        self.signal.step()

    def scatter(self):
        X, Y = [], []
        for d in "NESW":
            for c in self.q[d]:
                x, y = c.pos()
                X.append(x); Y.append(y)
        return X, Y

