from dataclasses import dataclass, field
import numpy as np
from typing import Dict, List, Tuple
from config import ArrivalCfg, SimCfg, LANE_OFF, ENTER, EXIT, STOP_LINE
from traffic_signal import FourSignalController, MultiSignalCfg

# ---------------------------------------------------------
# Trayectorias rectas
# ---------------------------------------------------------
def path_straight(d: str):
    if d == "N":  # arriba → abajo
        return lambda s: (+LANE_OFF,  ENTER - s * (ENTER + EXIT))
    if d == "S":  # abajo → arriba
        return lambda s: (-LANE_OFF, -ENTER + s * (ENTER + EXIT))
    if d == "E":  # derecha → izquierda
        return lambda s: ( ENTER - s * (ENTER + EXIT), -LANE_OFF)
    if d == "W":  # izquierda → derecha
        return lambda s: (-ENTER + s * (ENTER + EXIT), +LANE_OFF)
    raise ValueError(d)

# ---------------------------------------------------------
# Carro individual
# ---------------------------------------------------------
@dataclass
class Car:
    d: str
    s: float = 0.0
    committed: bool = False   # nuevo flag: ya entró al cruce con verde

    def pos(self) -> Tuple[float, float]:
        return path_straight(self.d)(self.s)

# ---------------------------------------------------------
# Simulador de intersección
# ---------------------------------------------------------
@dataclass
class IntersectionSim:
    arrivals: ArrivalCfg
    sim: SimCfg
    signal: FourSignalController
    rng: np.random.Generator = field(default_factory=lambda: np.random.default_rng(7))
    q: Dict[str, List[Car]] = field(default_factory=lambda: {k: [] for k in "NESW"})

    # -----------------------------------------------------
    # Spawning de autos según Poisson
    # -----------------------------------------------------
    def spawn(self):
        lam = dict(
            N=self.arrivals.lam_N,
            E=self.arrivals.lam_E,
            S=self.arrivals.lam_S,
            W=self.arrivals.lam_W
        )
        for d in "NESW":
            k = self.rng.poisson(lam[d])
            k = min(k, max(0, self.sim.max_queue - len(self.q[d])))
            for _ in range(k):
                self.q[d].append(Car(d))

    # -----------------------------------------------------
    # Decide → ya no hace nada con controlador adaptativo
    # -----------------------------------------------------
    def decide(self):
        pass

    # -----------------------------------------------------
    # STEP PRINCIPAL — mueve autos y actualiza semáforo
    # -----------------------------------------------------
    def step(self):

        self.spawn()
        self.decide()

        speed = self.sim.speed
        gap_s = self.sim.gap_s

        STOP_AT = STOP_LINE
        s_stop  = (ENTER - STOP_AT) / (ENTER + EXIT)
        s_eps   = 1e-3

        # mapeo de dirección -> índice de fase
        dir_idx = {"S": 2, "E": 0, "W": 3, "N": 1}

        # -------------------------------------------------
        # Movimiento por dirección
        # -------------------------------------------------
        for d in "NESW":
            arr = self.q[d]
            if not arr:
                continue

            green = self.signal.is_green(dir_idx[d])

            
            # ---------------------------------------------
            # LÍDER
            # ---------------------------------------------
            lead = arr[0]

            if not lead.committed:
                # Todavía NO está "comprometido" dentro del cruce
                if lead.s < s_stop - s_eps:
                    # se acerca a la línea de alto pero NO la pasa
                    if green:
                        lead.s = min(s_stop, lead.s + speed)
                    else:
                        lead.s = min(s_stop, lead.s + speed * 0.6)
                else:
                    # ya está justo en la línea de alto
                    if green:
                        # entra al cruce con verde → queda comprometido
                        lead.committed = True
                    # si está en rojo y no está comprometido, se queda en la línea
            else:
                # Ya entró al cruce con verde → sigue hasta salir, ignore el rojo
                lead.s = min(1.0, lead.s + speed)
                if lead.s >= 1.0:
                    arr.pop(0)


            # ---------------------------------------------
            # SEGUIDORES
            # ---------------------------------------------
            for i in range(1, len(arr)):
                car  = arr[i]
                prev = arr[i - 1]

                if prev.s <= s_stop:
                    # el de adelante aún no entra al cruce
                    if green:
                        target = min(s_stop - s_eps, prev.s - gap_s + speed * 0.3)
                    else:
                        target = min(s_stop - s_eps, prev.s - gap_s)
                else:
                    # el de adelante YA está cruzando
                    if green:
                        target = min(1.0, prev.s - gap_s)
                    else:
                        target = min(s_stop - s_eps, prev.s - gap_s)

                target = max(0.0, target)
                if car.s < target:
                    car.s = min(target, car.s + speed * 0.6)

        # -------------------------------------------------
        # Enviar tamaños de colas al controlador
        # -------------------------------------------------
        qsizes = {d: len(self.q[d]) for d in "NESW"}
        self.signal.update_queues(qsizes)

        # actualizar semáforo
        self.signal.step()

    # -----------------------------------------------------
    # posiciones para scatter plot
    # -----------------------------------------------------
    def scatter(self):
        X, Y = [], []
        for d in "NESW":
            for c in self.q[d]:
                x, y = c.pos()
                X.append(x)
                Y.append(y)
        return X, Y
