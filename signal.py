from dataclasses import dataclass
from config import SignalCfg

PHASE_NS = 0
PHASE_EW = 1

@dataclass
class TwoPhaseSignal:
    cfg: SignalCfg
    phase: int = PHASE_NS
    phase_t: int = 0
    amber_t: int = 0
    allred_t: int = 0

    def green_ns(self): return self.phase==PHASE_NS and self.amber_t==0 and self.allred_t==0
    def green_ew(self): return self.phase==PHASE_EW and self.amber_t==0 and self.allred_t==0

    def request_switch(self):
        if self.amber_t==0 and self.allred_t==0:
            self.amber_t = self.cfg.amber
            self.phase_t = 0

    def step(self):
        if self.amber_t>0:
            self.amber_t-=1
            if self.amber_t==0: self.allred_t=self.cfg.all_red
            return
        if self.allred_t>0:
            self.allred_t-=1
            if self.allred_t==0:
                self.phase = PHASE_EW if self.phase==PHASE_NS else PHASE_NS
            return
        self.phase_t+=1
