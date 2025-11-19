import matplotlib.pyplot as plt, matplotlib.animation as anim
from config import ArrivalCfg, SimCfg, SignalCfg, LANE_OFF, STOP_LINE
from intersection import IntersectionSim
from traffic_signal import FourSignalController, MultiSignalCfg

arr = ArrivalCfg()
sim = SimCfg()
sig = FourSignalController(MultiSignalCfg(), tick_ms=sim.realtime_ms)
world = IntersectionSim(arr, sim, sig)

fig,ax=plt.subplots(figsize=(6,6))
ax.set_xlim(-1.8,1.8); ax.set_ylim(-1.8,1.8); ax.axis("off")
ax.set_title("Traffic Light 4 Intersections")

def draw_roads():
    ax.plot([-1.6,1.6],[-LANE_OFF,-LANE_OFF],lw=10,alpha=0.12)
    ax.plot([-1.6,1.6],[ LANE_OFF, LANE_OFF],lw=10,alpha=0.12)
    ax.plot([ LANE_OFF, LANE_OFF],[-1.6,1.6],lw=10,alpha=0.12)
    ax.plot([-LANE_OFF,-LANE_OFF],[-1.6,1.6],lw=10,alpha=0.12)
draw_roads()

dots,=ax.plot([],[],"o",ms=5)

# semáforos: 4 postes, 2 verticales (N,S) y 2 horizontales (E,W)
LIGHT_R, LIGHT_Y, LIGHT_G = "#d9534f", "#f0ad4e", "#5cb85c"
POLE_OFF, HEAD_GAP, RAD = 0.18, 0.10, 0.06

def add_triplet_vertical(x, y):
    r = plt.Circle((x, y + HEAD_GAP), RAD, fc="grey", ec="black")
    yel = plt.Circle((x, y), RAD, fc="grey", ec="black")
    g = plt.Circle((x, y - HEAD_GAP), RAD, fc="grey", ec="black")
    ax.add_patch(r); ax.add_patch(yel); ax.add_patch(g)
    return (r, yel, g)

def add_triplet_horizontal(x, y):
    r = plt.Circle((x - HEAD_GAP, y), RAD, fc="grey", ec="black")
    yel = plt.Circle((x, y), RAD, fc="grey", ec="black")
    g = plt.Circle((x + HEAD_GAP, y), RAD, fc="grey", ec="black")
    ax.add_patch(r); ax.add_patch(yel); ax.add_patch(g)
    return (r, yel, g)

# posiciones (coordenadas respecto al centro)
N_pos = (+LANE_OFF + POLE_OFF, +STOP_LINE + POLE_OFF)
S_pos = (-LANE_OFF - POLE_OFF, -STOP_LINE - POLE_OFF)
E_pos = (+STOP_LINE + POLE_OFF, -LANE_OFF - POLE_OFF)
W_pos = (-STOP_LINE - POLE_OFF, +LANE_OFF + POLE_OFF)

lights = {
    "N": add_triplet_vertical(*N_pos),
    "S": add_triplet_vertical(*S_pos),
    "E": add_triplet_horizontal(*E_pos),
    "W": add_triplet_horizontal(*W_pos),
}

def paint(triplet, state):
    r, y, g = triplet
    r.set_facecolor(LIGHT_R if state == "red" else "grey")
    y.set_facecolor(LIGHT_Y if state == "amber" else "grey")
    g.set_facecolor(LIGHT_G if state == "green" else "grey")

def update(_):
    world.step()

    # mapeo 1=S→N, 2=E→W, 3=W→E, 4=N→S
    order = {"S": 2, "E": 0, "W": 3, "N": 1}

    states = {}
    if world.signal.amber_t > 0:
        states = {k: "amber" for k in "NESW"}
    elif world.signal.allred_t > 0:
        states = {k: "red" for k in "NESW"}
    else:
        for k in "NESW":
            states[k] = "green" if world.signal.is_green(order[k]) else "red"

    for k, v in lights.items():
        paint(v, states[k])

    X, Y = world.scatter()
    dots.set_data(X, Y)

    # opcional: ver la fase en la ventana
    ax.set_title(f"Traffic Light 4 Intersections — Fase {world.signal.phase+1}")
    return [dots] + [p for t in lights.values() for p in t]

ani = anim.FuncAnimation(fig, update, interval=sim.realtime_ms, blit=True, cache_frame_data=False)
plt.show()
