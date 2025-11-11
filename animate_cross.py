import matplotlib.pyplot as plt, matplotlib.animation as anim
from config import ArrivalCfg, SimCfg, SignalCfg, LANE_OFF, STOP_LINE
from traffic_signal import TwoPhaseSignal, PHASE_NS, PHASE_EW
from intersection import IntersectionSim

arr=ArrivalCfg(); sig=TwoPhaseSignal(SignalCfg()); sim=SimCfg()
world=IntersectionSim(arr,sim,sig)

fig,ax=plt.subplots(figsize=(6,6))
ax.set_xlim(-1.8,1.8); ax.set_ylim(-1.8,1.8); ax.axis("off")
ax.set_title("Straight-only Cross (2-phase with Amber & All-Red)")

def draw_roads():
    ax.plot([-1.6,1.6],[-LANE_OFF,-LANE_OFF],lw=10,alpha=0.12)
    ax.plot([-1.6,1.6],[ LANE_OFF, LANE_OFF],lw=10,alpha=0.12)
    ax.plot([ LANE_OFF, LANE_OFF],[-1.6,1.6],lw=10,alpha=0.12)
    ax.plot([-LANE_OFF,-LANE_OFF],[-1.6,1.6],lw=10,alpha=0.12)
draw_roads()

dots,=ax.plot([],[],"o",ms=5)

LIGHT_R,LIGHT_Y,LIGHT_G="#d9534f","#f0ad4e","#5cb85c"
POLE_OFF,HEAD_GAP,RAD=0.18,0.10,0.06
def add_triplet(x,y):
    r=plt.Circle((x,y+HEAD_GAP),RAD,fc="grey",ec="black"); ax.add_patch(r)
    yel=plt.Circle((x,y),RAD,fc="grey",ec="black"); ax.add_patch(yel)
    g=plt.Circle((x,y-HEAD_GAP),RAD,fc="grey",ec="black"); ax.add_patch(g)
    return (r,yel,g)

N_pos=(+LANE_OFF+POLE_OFF,+STOP_LINE+POLE_OFF)
S_pos=(-LANE_OFF-POLE_OFF,-STOP_LINE-POLE_OFF)
E_pos=(+STOP_LINE+POLE_OFF,-LANE_OFF-POLE_OFF)
W_pos=(-STOP_LINE-POLE_OFF,+LANE_OFF+POLE_OFF)
lights={"N":add_triplet(*N_pos),"S":add_triplet(*S_pos),"E":add_triplet(*E_pos),"W":add_triplet(*W_pos)}

def paint(t,state):
    r,y,g=t
    r.set_facecolor(LIGHT_R if state=="red" else "grey")
    y.set_facecolor(LIGHT_Y if state=="amber" else "grey")
    g.set_facecolor(LIGHT_G if state=="green" else "grey")

def update(_):
    world.step()
    if world.signal.amber_t>0: states={k:"amber" for k in "NESW"}
    elif world.signal.allred_t>0: states={k:"red" for k in "NESW"}
    else:
        if world.signal.phase==PHASE_NS: states={"N":"green","S":"green","E":"red","W":"red"}
        else: states={"N":"red","S":"red","E":"green","W":"green"}
    for k,v in lights.items(): paint(v,states[k])
    X,Y=world.scatter(); dots.set_data(X,Y); return [dots]+[p for t in lights.values() for p in t]

ani = anim.FuncAnimation(fig, update, interval=sim.realtime_ms, blit=True, cache_frame_data=False)
plt.show()
