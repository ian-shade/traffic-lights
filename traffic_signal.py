from dataclasses import dataclass

@dataclass
class MultiSignalCfg:
    # tiempos en segundos "reales"
    min_green_s: float = 8.0     # mínimo en verde
    max_green_s: float = 30.0    # máximo en verde
    amber_s: float = 3.0         # ámbar
    all_red_s: float = 1.0       # todo rojo

class FourSignalController:
    """
    Controlador adaptativo 4-fases.
    Fases (índices) 0..3 corresponden a direcciones S, E, W, N (en ese orden).
    Decide a qué fase darle verde según las colas y respeta tiempos mínimos/máximos.
    """
    def __init__(self, cfg: MultiSignalCfg, tick_ms: int):
        self.cfg = cfg
        self.tick_ms = tick_ms

        # Orden fija de direcciones asociadas a índices 0..3
        self.order = ["E", "N", "S", "W"]  # 0=S, 1=E, 2=W, 3=N

        # Estado de la fase
        self.phase_idx = 0     # índice actual en self.order
        self.phase_t = 0       # ticks que lleva en verde
        self.amber_t = 0       # ticks restantes de ámbar
        self.allred_t = 0      # ticks restantes de todo rojo

        # Colas por dirección (IntersectionSim las actualiza)
        self.qsizes = {d: 0 for d in "NESW"}

        # Conversión de segundos a ticks
        self.min_green_ticks = max(1, int(self.cfg.min_green_s * 1000 / self.tick_ms))
        self.max_green_ticks = max(self.min_green_ticks, int(self.cfg.max_green_s * 1000 / self.tick_ms))
        self.amber_ticks     = max(1, int(self.cfg.amber_s     * 1000 / self.tick_ms))
        self.allred_ticks    = max(1, int(self.cfg.all_red_s   * 1000 / self.tick_ms))

    @property
    def phase(self):
        """Compatibilidad con código que usa .phase (1..4 al sumarle 1)."""
        return self.phase_idx

    def current_dir(self) -> str:
        return self.order[self.phase_idx]

    def update_queues(self, qsizes):
        """IntersectionSim llama esto cada tick con len(cola) de N,E,S,W."""
        self.qsizes = qsizes

    def is_green(self, idx: int) -> bool:
        """True si la fase idx está verde en este tick."""
        return (
            self.amber_t == 0 and
            self.allred_t == 0 and
            idx == self.phase_idx
        )

    def step(self):
        # Manejo de ámbar
        if self.amber_t > 0:
            self.amber_t -= 1
            if self.amber_t == 0:
                self.allred_t = self.allred_ticks
            return

        # Manejo de todo rojo
        if self.allred_t > 0:
            self.allred_t -= 1
            if self.allred_t == 0:
                # al salir del all-red, empezamos a contar nuevo verde
                self.phase_t = 0
            return

        # Estamos en verde de alguna dirección
        self.phase_t += 1

        cur_dir = self.current_dir()
        cur_q   = self.qsizes.get(cur_dir, 0)

        # Dirección con más coches
        max_dir = max(self.qsizes, key=self.qsizes.get)
        max_q   = self.qsizes[max_dir]

        need_change = False

        # Regla 1: si ya excedimos el verde máximo, cambiamos sí o sí
        if self.phase_t >= self.max_green_ticks:
            need_change = True
        else:
            # Regla 2: si otra cola es claramente mayor (al menos +2 coches)
            if max_q >= cur_q + 2:
                need_change = True
            # Regla 3: si la actual no tiene coches y otra sí
            if cur_q == 0 and max_q > 0:
                need_change = True

        if not need_change:
            return

        # Si todas las colas son 0, no tiene sentido cambiar
        if max_q == 0:
            return

        # Cambiar a la dirección con mayor cola
        self.phase_idx = self.order.index(max_dir)
        self.phase_t = 0
        self.amber_t = self.amber_ticks
