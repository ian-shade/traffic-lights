import glob
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

os.makedirs("results", exist_ok=True)

FILES = sorted(glob.glob("metrics_*.csv"))

if not FILES:
    raise FileNotFoundError("No metrics_*.csv found. Run simulation and export metrics first.")

def pretty(path: str) -> str:
    base = os.path.splitext(os.path.basename(path))[0]
    return base.replace("metrics_", "").replace("_", " ").title()

def find_col(df: pd.DataFrame, candidates: list) -> str:
    for c in candidates:
        if c in df.columns:
            return c
    return None

def safe_val(df: pd.DataFrame, col: str, func):
    if col is None or col not in df.columns or df.empty:
        return None
    return func(df[col])

dfs = {f: pd.read_csv(f) for f in FILES}

TIME_COLS = ["time_s", "time", "t", "seconds"]
TOTAL_QUEUE_COLS = ["total_queue", "queue_total", "totalQueue", "queue"]
VIP_QUEUE_COLS = ["vip_queue", "queue_vip", "vipQueue"]
WAIT_COLS = ["avg_wait", "avg_wait_s", "mean_wait_s"]

plt.figure(figsize=(10, 6))
for f, df in dfs.items():
    tcol = find_col(df, TIME_COLS)
    qcol = find_col(df, TOTAL_QUEUE_COLS)
    if tcol and qcol:
        plt.plot(df[tcol], df[qcol], label=pretty(f), linewidth=2)

plt.xlabel("Time (s)", fontsize=12)
plt.ylabel("Total Queue Length", fontsize=12)
plt.title("Controller Comparison: Total Queue Over Time", fontsize=14, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("results/total_queue_time.png", dpi=200)
plt.close()

plt.figure(figsize=(10, 6))
for f, df in dfs.items():
    tcol = find_col(df, TIME_COLS)
    vcol = find_col(df, VIP_QUEUE_COLS)
    if tcol and vcol:
        plt.plot(df[tcol], df[vcol], label=pretty(f), linewidth=2)

plt.xlabel("Time (s)", fontsize=12)
plt.ylabel("VIP Queue Length", fontsize=12)
plt.title("Controller Comparison: VIP Queue Over Time", fontsize=14, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("results/vip_queue_time.png", dpi=200)
plt.close()

rows = []
for f, df in dfs.items():
    tcol = find_col(df, TIME_COLS)
    qcol = find_col(df, TOTAL_QUEUE_COLS)
    vcol = find_col(df, VIP_QUEUE_COLS)
    wcol = find_col(df, WAIT_COLS)

    row = {
        "controller": pretty(f),
        "avg_total_queue": safe_val(df, qcol, lambda x: x.mean()),
        "p95_total_queue": safe_val(df, qcol, lambda x: x.quantile(0.95)),
        "max_total_queue": safe_val(df, qcol, lambda x: x.max()),
        "avg_vip_queue": safe_val(df, vcol, lambda x: x.mean()),
        "avg_wait_time": safe_val(df, wcol, lambda x: x.iloc[-1] if len(x) > 0 else 0),
        "duration_s": safe_val(df, tcol, lambda x: x.iloc[-1] if len(x) > 0 else 0)
    }

    if "phase" in df.columns:
        switches = (df["phase"] != df["phase"].shift()).sum() - 1
        row["total_switches"] = max(0, switches)

    if qcol and tcol:
        row["cumulative_queue"] = np.trapz(df[qcol], df[tcol])

    rows.append(row)

summary = pd.DataFrame(rows)

sort_cols = [c for c in ["avg_total_queue", "p95_total_queue"] if c in summary.columns]
if sort_cols:
    summary = summary.sort_values(sort_cols, na_position="last")

summary.to_csv("results/comparison_summary.csv", index=False)

controllers = summary["controller"].tolist()
avg_queue = summary["avg_total_queue"].tolist()
max_queue = summary["max_total_queue"].tolist()

x = np.arange(len(controllers))
width = 0.35

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(x - width/2, avg_queue, width, label='Average Queue', color='steelblue')
ax.bar(x + width/2, max_queue, width, label='Max Queue', color='coral')

ax.set_xlabel('Controller', fontsize=12)
ax.set_ylabel('Queue Length (cars)', fontsize=12)
ax.set_title('Controller Performance Comparison', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(controllers, rotation=15, ha='right')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig("results/bar_comparison.png", dpi=200)
plt.close()

if "total_switches" in summary.columns:
    fig, ax = plt.subplots(figsize=(10, 6))
    switches = summary["total_switches"].tolist()
    ax.bar(controllers, switches, color='teal')
    ax.set_xlabel('Controller', fontsize=12)
    ax.set_ylabel('Total Phase Switches', fontsize=12)
    ax.set_title('Phase Switch Count by Controller', fontsize=14, fontweight='bold')
    ax.set_xticklabels(controllers, rotation=15, ha='right')
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig("results/switch_count.png", dpi=200)
    plt.close()

plt.figure(figsize=(10, 6))
for f, df in dfs.items():
    tcol = find_col(df, TIME_COLS)
    if tcol and "phase" in df.columns:
        switches = (df["phase"] != df["phase"].shift()).cumsum()
        plt.plot(df[tcol], switches, label=pretty(f), linewidth=2)

plt.xlabel("Time (s)", fontsize=12)
plt.ylabel("Cumulative Switches", fontsize=12)
plt.title("Phase Switch Behavior Over Time", fontsize=14, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("results/switches_over_time.png", dpi=200)
plt.close()

if "cumulative_queue" in summary.columns:
    fig, ax = plt.subplots(figsize=(10, 6))
    cumulative = summary["cumulative_queue"].tolist()
    ax.bar(controllers, cumulative, color='indianred')
    ax.set_xlabel('Controller', fontsize=12)
    ax.set_ylabel('Cumulative Queue-Time (car·seconds)', fontsize=12)
    ax.set_title('Total Congestion Burden', fontsize=14, fontweight='bold')
    ax.set_xticklabels(controllers, rotation=15, ha='right')
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig("results/cumulative_queue.png", dpi=200)
    plt.close()

fig, axes = plt.subplots(2, 3, figsize=(15, 10))
axes = axes.flatten()

for idx, (f, df) in enumerate(dfs.items()):
    if idx >= 6:
        break
    qcol = find_col(df, TOTAL_QUEUE_COLS)
    if qcol:
        axes[idx].hist(df[qcol], bins=20, color='skyblue', edgecolor='black', alpha=0.7)
        axes[idx].set_title(pretty(f), fontweight='bold')
        axes[idx].set_xlabel('Queue Length')
        axes[idx].set_ylabel('Frequency')
        axes[idx].grid(True, alpha=0.3)

for idx in range(len(dfs), 6):
    axes[idx].axis('off')

plt.suptitle('Queue Length Distribution by Controller', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig("results/queue_distributions.png", dpi=200)
plt.close()

fig, axes = plt.subplots(1, len(dfs), figsize=(4*len(dfs), 5))
if len(dfs) == 1:
    axes = [axes]

for idx, (f, df) in enumerate(dfs.items()):
    qcol = find_col(df, TOTAL_QUEUE_COLS)
    if qcol:
        bp = axes[idx].boxplot([df[qcol]], labels=[''], patch_artist=True)
        for patch in bp['boxes']:
            patch.set_facecolor('lightgreen')
        axes[idx].set_title(pretty(f), fontweight='bold')
        axes[idx].set_ylabel('Queue Length')
        axes[idx].grid(True, alpha=0.3, axis='y')

plt.suptitle('Queue Length Distribution (Box Plots)', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig("results/queue_boxplots.png", dpi=200)
plt.close()

has_per_direction = any("qN" in df.columns for df in dfs.values())

if has_per_direction:
    direction_stats = []
    for f, df in dfs.items():
        if all(col in df.columns for col in ["qN", "qS", "qE", "qW"]):
            direction_stats.append({
                "controller": pretty(f),
                "avg_north": df["qN"].mean(),
                "avg_south": df["qS"].mean(),
                "avg_east": df["qE"].mean(),
                "avg_west": df["qW"].mean(),
                "std_dev": np.std([df["qN"].mean(), df["qS"].mean(), df["qE"].mean(), df["qW"].mean()])
            })

    if direction_stats:
        dir_df = pd.DataFrame(direction_stats)
        dir_df.to_csv("results/direction_fairness.csv", index=False)

        fig, ax = plt.subplots(figsize=(10, 6))
        x = np.arange(len(dir_df))
        width = 0.2

        ax.bar(x - 1.5*width, dir_df["avg_north"], width, label='North', color='#1f77b4')
        ax.bar(x - 0.5*width, dir_df["avg_south"], width, label='South', color='#ff7f0e')
        ax.bar(x + 0.5*width, dir_df["avg_east"], width, label='East', color='#2ca02c')
        ax.bar(x + 1.5*width, dir_df["avg_west"], width, label='West', color='#d62728')

        ax.set_xlabel('Controller', fontsize=12)
        ax.set_ylabel('Average Queue Length', fontsize=12)
        ax.set_title('Per-Direction Queue Fairness', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(dir_df["controller"], rotation=15, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        plt.savefig("results/direction_fairness.png", dpi=200)
        plt.close()

        for f, df in dfs.items():
            if all(col in df.columns for col in ["qN", "qS", "qE", "qW", "time_s"]):
                fig, ax = plt.subplots(figsize=(12, 6))
                ax.plot(df["time_s"], df["qN"], label='North', linewidth=2)
                ax.plot(df["time_s"], df["qS"], label='South', linewidth=2)
                ax.plot(df["time_s"], df["qE"], label='East', linewidth=2)
                ax.plot(df["time_s"], df["qW"], label='West', linewidth=2)
                ax.set_xlabel('Time (s)', fontsize=12)
                ax.set_ylabel('Queue Length', fontsize=12)
                ax.set_title(f'{pretty(f)}: Per-Direction Queues Over Time', fontsize=14, fontweight='bold')
                ax.legend()
                ax.grid(True, alpha=0.3)
                plt.tight_layout()
                fname = f.replace("metrics_", "").replace(".csv", "")
                plt.savefig(f"results/direction_{fname}.png", dpi=200)
                plt.close()

if "avg_wait_time" in summary.columns and summary["avg_wait_time"].notna().any():
    fig, ax = plt.subplots(figsize=(10, 6))
    wait_times = summary["avg_wait_time"].tolist()
    ax.bar(controllers, wait_times, color='mediumpurple')
    ax.set_xlabel('Controller', fontsize=12)
    ax.set_ylabel('Average Wait Time (ms)', fontsize=12)
    ax.set_title('Average Wait Time Per Car', fontsize=14, fontweight='bold')
    ax.set_xticklabels(controllers, rotation=15, ha='right')
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig("results/avg_wait_time.png", dpi=200)
    plt.close()

print("\n" + "="*60)
print("COMPARISON SUMMARY")
print("="*60)
print(summary.to_string(index=False))
print("\n" + "="*60)
print("All plots saved to results/ folder:")
print("  - total_queue_time.png")
print("  - vip_queue_time.png")
print("  - bar_comparison.png")
print("  - switch_count.png")
print("  - switches_over_time.png")
print("  - cumulative_queue.png")
print("  - queue_distributions.png")
print("  - queue_boxplots.png")
if has_per_direction:
    print("  - direction_fairness.png")
    print("  - direction_*.png (per controller)")
if "avg_wait_time" in summary.columns:
    print("  - avg_wait_time.png")
print("\nCSV files:")
print("  - comparison_summary.csv")
if has_per_direction:
    print("  - direction_fairness.csv")
print("="*60)
