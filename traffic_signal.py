from dataclasses import dataclass

@dataclass
class MultiSignalCfg:
    green: int = 12
    amber: int = 3
    all_red: int = 1

class FourSignalController:
    """
    Cuatro semáforos independientes.
    Fase 0=1(S→N), 1=2(E→W), 2=3(W→E), 3=4(N→S) y se repite.
    """
    def __init__(self, cfg: MultiSignalCfg):
        self.cfg = cfg
        self.phase = 0
        self.timer = 0
        self.amber_t = 0
        self.allred_t = 0

    def is_green(self, idx: int) -> bool:
        return self.phase == idx and self.amber_t == 0 and self.allred_t == 0

    def is_amber(self, idx: int) -> bool:
        return self.phase == idx and self.amber_t > 0

    def step(self):
        if self.amber_t > 0:
            self.amber_t -= 1
            if self.amber_t == 0:
                self.allred_t = self.cfg.all_red
            return
        if self.allred_t > 0:
            self.allred_t -= 1
            if self.allred_t == 0:
                self.phase = (self.phase + 1) % 4
            return

        self.timer += 1
        if self.timer >= self.cfg.green:
            self.timer = 0
            self.amber_t = self.cfg.amber
