import sys
import os
import time
os.environ['SDL_VIDEODRIVER'] = 'dummy'

import pygame
from simulation import TrafficSimulation

os.makedirs("metrics", exist_ok=True)

controllers = ["actuated", "max_pressure", "q_learning"]
spawn_rate = 2.0
duration_s = 120

print("="*60)
print("GENERATING METRICS FOR ALL CONTROLLERS")
print("="*60)
print(f"Configuration: spawn_rate={spawn_rate}s, duration={duration_s}s\n")

for ctrl in controllers:
    print(f"Running {ctrl}...", end=" ", flush=True)

    pygame.init()
    sim = TrafficSimulation()
    sim.controller_name = ctrl
    sim._apply_controller(ctrl)
    sim.spawn_rate = spawn_rate

    start_time = time.time()
    while sim.current_time < duration_s * 1000 and sim.running:
        delta_time = 16.67
        sim.update(delta_time)

    elapsed = time.time() - start_time

    filename = f"metrics/metrics_{ctrl}.csv"
    sim.export_metrics(filename)

    print(f"done ({elapsed:.1f}s)")

    pygame.quit()

print("\n" + "="*60)
print("COMPLETE")
print("="*60)
print("\nGenerated files in metrics/ folder:")
for ctrl in controllers:
    print(f"  - metrics_{ctrl}.csv")

print("\nNext step:")
print("  Run: python compare_results.py")
print("="*60)
