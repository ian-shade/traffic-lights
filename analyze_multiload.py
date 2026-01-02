import glob
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

os.makedirs("results/multiload", exist_ok=True)

light_files = sorted(glob.glob("metrics/metrics_*_light.csv"))
normal_files = sorted(glob.glob("metrics/metrics_*_normal.csv"))
heavy_files = sorted(glob.glob("metrics/metrics_*_heavy.csv"))

if not (light_files and normal_files and heavy_files):
    print("Error: Run run_multiload_experiments.py first to generate data")
    exit(1)

def extract_controller(filename):
    base = os.path.basename(filename)
    return base.replace("metrics_", "").replace("_light.csv", "").replace("_normal.csv", "").replace("_heavy.csv", "").replace("_", " ").title()

def analyze_load(files, load_name):
    results = []
    for f in files:
        df = pd.read_csv(f)
        ctrl = extract_controller(f)

        switches = 0
        if "phase" in df.columns:
            switches = (df["phase"] != df["phase"].shift()).sum() - 1

        cumulative_queue = 0
        if "total_queue" in df.columns and "time_s" in df.columns:
            cumulative_queue = np.trapz(df["total_queue"], df["time_s"])

        avg_wait = 0
        if "avg_wait" in df.columns and len(df) > 0:
            avg_wait = df["avg_wait"].iloc[-1]

        results.append({
            "controller": ctrl,
            "load": load_name,
            "avg_queue": df["total_queue"].mean() if "total_queue" in df.columns else 0,
            "max_queue": df["total_queue"].max() if "total_queue" in df.columns else 0,
            "p95_queue": df["total_queue"].quantile(0.95) if "total_queue" in df.columns else 0,
            "switches": switches,
            "cumulative_queue": cumulative_queue,
            "avg_wait": avg_wait
        })
    return results

light_results = analyze_load(light_files, "Light")
normal_results = analyze_load(normal_files, "Normal")
heavy_results = analyze_load(heavy_files, "Heavy")

all_results = pd.DataFrame(light_results + normal_results + heavy_results)
all_results.to_csv("results/multiload/multiload_summary.csv", index=False)

controllers = sorted(all_results["controller"].unique())
loads = ["Light", "Normal", "Heavy"]

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

x = np.arange(len(controllers))
width = 0.25

for ax, metric, ylabel in zip(
    axes.flat,
    ["avg_queue", "max_queue", "switches", "avg_wait"],
    ["Average Queue Length", "Max Queue Length", "Total Switches", "Avg Wait Time (ms)"]
):
    light_vals = [all_results[(all_results["controller"]==c) & (all_results["load"]=="Light")][metric].values[0] for c in controllers]
    normal_vals = [all_results[(all_results["controller"]==c) & (all_results["load"]=="Normal")][metric].values[0] for c in controllers]
    heavy_vals = [all_results[(all_results["controller"]==c) & (all_results["load"]=="Heavy")][metric].values[0] for c in controllers]

    ax.bar(x - width, light_vals, width, label='Light', color='lightblue')
    ax.bar(x, normal_vals, width, label='Normal', color='steelblue')
    ax.bar(x + width, heavy_vals, width, label='Heavy', color='darkblue')

    ax.set_ylabel(ylabel, fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels(controllers, rotation=20, ha='right', fontsize=9)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

plt.suptitle('Multi-Load Performance Comparison', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig("results/multiload/multiload_comparison.png", dpi=200)
plt.close()

for ctrl in controllers:
    ctrl_data = all_results[all_results["controller"] == ctrl]

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    metrics = [
        ("avg_queue", "Average Queue Length"),
        ("switches", "Total Switches"),
        ("avg_wait", "Avg Wait Time (ms)")
    ]

    for ax, (metric, ylabel) in zip(axes, metrics):
        vals = [ctrl_data[ctrl_data["load"]==load][metric].values[0] for load in loads]
        ax.bar(loads, vals, color=['lightblue', 'steelblue', 'darkblue'])
        ax.set_ylabel(ylabel)
        ax.set_title(f"{ctrl}")
        ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    fname = ctrl.lower().replace(" ", "_")
    plt.savefig(f"results/multiload/{fname}_loads.png", dpi=200)
    plt.close()

print("\n" + "="*70)
print("MULTI-LOAD ANALYSIS COMPLETE")
print("="*70)
print("\nSummary Statistics:")
print(all_results.to_string(index=False))

print("\n" + "="*70)
print("Files saved to results/multiload/:")
print("  - multiload_summary.csv")
print("  - multiload_comparison.png")
for ctrl in controllers:
    fname = ctrl.lower().replace(" ", "_")
    print(f"  - {fname}_loads.png")
print("="*70)
