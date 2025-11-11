from dataclasses import dataclass, field
import numpy as np
from typing import Dict, List, Tuple
from config import ArrivalCfg, SimCfg, LANE_OFF, ENTER, EXIT, STOP_LINE, STOP_MARGIN
from traffic_signal import TwoPhaseSignal

def path_straight(d):
    if d=="N": return lambda s:(+LANE_OFF, ENTER - s*(ENTER+EXIT))
    if d=="S": return lambda s:(-LANE_OFF,-ENTER + s*(ENTER+EXIT))
    if d=="E": return lambda s:(ENTER - s*(ENTER+EXIT), -LANE_OFF)
    if d=="W": return lambda s:(-ENTER + s*(ENTER+EXIT), +LANE_OFF)

@dataclass
class Car:
    d: str
    s: float=0.0
    def pos(self): return path_straight(self.d)(self.s)

@dataclass
class IntersectionSim:
    arrivals: ArrivalCfg
    sim: SimCfg
    signal: TwoPhaseSignal
    rng: np.random.Generator = field(default_factory=lambda: np.random.default_rng(7))
    q: Dict[str, List[Car]] = field(default_factory=lambda: {k:[] for k in "NESW"})

    def spawn(self):
        lam=dict(N=self.arrivals.lam_N,E=self.arrivals.lam_E,S=self.arrivals.lam_S,W=self.arrivals.lam_W)
        for d in "NESW":
            k=self.rng.poisson(lam[d])
            k=min(k,max(0,self.sim.max_queue-len(self.q[d])))
            for _ in range(k): self.q[d].append(Car(d))

    def decide(self):
        if self.signal.amber_t==0 and self.signal.allred_t==0 and self.signal.phase_t>=self.signal.cfg.min_green:
            self.signal.request_switch()

    def step(self):
        self.spawn()
        self.decide()
        self.signal.step()

        speed = self.sim.speed
        gap_s = self.sim.gap_s

        # --- s en el que se ubica la línea de alto para cualquier dirección ---
        # Para nuestras trayectorias rectas:
        # N:  y =  ENTER - s*(ENTER+EXIT)  y_stop = +STOP_LINE
        # S:  y = -ENTER + s*(ENTER+EXIT)  y_stop = -STOP_LINE
        # E:  x =  ENTER - s*(ENTER+EXIT)  x_stop = +STOP_LINE
        # W:  x = -ENTER + s*(ENTER+EXIT)  x_stop = -STOP_LINE
        # => en todos los casos: s_stop = (ENTER - STOP_LINE) / (ENTER + EXIT)
        STOP_AT = STOP_LINE + STOP_MARGIN
        s_stop = (ENTER - STOP_LINE) / (ENTER + EXIT)
        s_eps  = 1e-3

        for d in "NESW":
            arr = self.q[d]
            if not arr:
                continue

            # ¿esta dirección tiene verde ahora?
            green = (self.signal.green_ns() if d in ("N","S") else self.signal.green_ew())

            # ----- líder -----
            lead = arr[0]
            if lead.s < s_stop - s_eps:
                # puede acercarse a la línea de alto aunque esté en rojo (más lento)
                lead.s = min(s_stop, lead.s + speed * 0.6)
            else:
                if green:
                    # luz verde: puede cruzar el centro
                    lead.s = min(1.0, lead.s + speed)
                    if lead.s >= 1.0:
                        arr.pop(0)
                else:
                    # luz roja: se queda EXACTO en la línea de alto
                    lead.s = min(lead.s, s_stop)

            # ----- seguidores -----
            for i in range(1, len(arr)):
                car = arr[i]
                prev = arr[i-1]
                # nunca pasar la línea de alto ni subirse al coche de adelante
                target = min(s_stop - s_eps, prev.s - gap_s)
                # si la cola está muy corta, mantenlos atrás sin chocar numéricamente
                target = max(0.0, target)
                if car.s < target:
                    # se aproximan más lento que el líder para que no “empujen”
                    car.s = min(target, car.s + speed * 0.6)


    def scatter(self):
        X,Y=[],[]
        for d in "NESW":
            for c in self.q[d]:
                x,y=c.pos(); X.append(x); Y.append(y)
        return X,Y

