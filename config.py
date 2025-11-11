from dataclasses import dataclass

LANE_OFF = 0.14
ENTER = 1.20
EXIT = 1.20
STOP_LINE = 0.14   
STOP_MARGIN = 0.35    

@dataclass
class ArrivalCfg:
    lam_N: float = 0.10
    lam_E: float = 0.12
    lam_S: float = 0.08
    lam_W: float = 0.08

@dataclass
class SignalCfg:
    min_green: int = 12
    amber: int = 3
    all_red: int = 1

@dataclass
class SimCfg:
    realtime_ms: int = 500   
    speed: float  = 0.035    
    gap_s: float  = 0.06
    max_queue: int = 12

