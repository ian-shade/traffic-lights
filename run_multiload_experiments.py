import sys
import os
import time
os.environ['SDL_VIDEODRIVER'] = 'dummy'

import pygame
from simulation import TrafficSimulation

configs = [
    {"name": "light", "spawn_rate": 3.5, "duration": 120},
    {"name": "normal", "spawn_rate": 2.0, "duration": 120},
    {"name": "heavy", "spawn_rate": 1.0, "duration": 120},
]

controllers = ["fixed_time", "actuated", "max_pressure", "fuzzy", "q_learning"]

print("="*60)
print("MULTI-LOAD TRAFFIC SIMULATION EXPERIMENT")
print("="*60)

for config in configs:
    load_name = config["name"]
    spawn_rate = config["spawn_rate"]
    duration_s = config["duration"]

    print(f"\n{'='*60}")
    print(f"LOAD: {load_name.upper()} (spawn_rate={spawn_rate}s, duration={duration_s}s)")
    print(f"{'='*60}\n")

    for ctrl in controllers:
        print(f"  Running {ctrl}...", end=" ", flush=True)

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

        filename = f"metrics_{ctrl}_{load_name}.csv"
        sim.export_metrics(filename)

        print(f"done ({elapsed:.1f}s real-time)")

        pygame.quit()

print("\n" + "="*60)
print("EXPERIMENT COMPLETE")
print("="*60)
print("\nGenerated files:")
for config in configs:
    for ctrl in controllers:
        print(f"  - metrics_{ctrl}_{config['name']}.csv")

print("\nNext steps:")
print("  1. Organize files: mkdir -p results/light results/normal results/heavy")
print("  2. Move files: mv metrics_*_light.csv results/light/")
print("  3. Run compare_results.py in each folder")
print("  4. Compare across loads")
print("="*60)
