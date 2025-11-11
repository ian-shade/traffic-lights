from dataclasses import dataclass, field
import numpy as np
from typing import Dict, List, Tuple
from config import ArrivalCfg, SimCfg, LANE_OFF, ENTER, EXIT, STOP_LINE
from signal import TwoPhaseSignal

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
        self.spawn(); self.decide(); self.signal.step()
        speed=self.sim.speed; gap=self.sim.gap_s
        for d in "NESW":
            arr=self.q[d]
            if not arr: continue
            lead=arr[0]; x,y=lead.pos()
            near=((d=="N" and y<=STOP_LINE) or (d=="S" and y>=-STOP_LINE) or
                  (d=="E" and x<=STOP_LINE) or (d=="W" and x>=-STOP_LINE))
            green=self.signal.green_ns() if d in("N","S") else self.signal.green_ew()
            if not near or green:
                lead.s=min(1.0,lead.s+speed)
                if lead.s>=1.0: arr.pop(0)
            for i in range(1,len(arr)):
                car=arr[i]; target=min(1.0-1e-3,i*gap)
                if car.s<target: car.s=min(target,car.s+speed*0.6)

    def scatter(self):
        X,Y=[],[]
        for d in "NESW":
            for c in self.q[d]:
                x,y=c.pos(); X.append(x); Y.append(y)
        return X,Y

