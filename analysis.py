# analysis.py
#
# This script loads the metrics generated during Q-learning training
# and produces simple plots to help visualize how the agent improved.
#
# It also prints a small statistics summary that can be used in the report.

import json
import matplotlib.pyplot as plt
import numpy as np


def load_metrics():
    with open("training_metrics.json", "r") as f:
        return json.load(f)


def plot_metric(values, title, ylabel, filename):
    plt.figure(figsize=(10, 4))
    plt.plot(values, linewidth=1.3)
    plt.title(title)
    plt.xlabel("Episode")
    plt.ylabel(ylabel)
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(filename)
    print(f"[Saved] {filename}")
    plt.show()


def print_summary(name, data):
    data = np.array(data)
    print(f"\n{name} Summary")
    print("-" * 40)
    print(f"Mean:        {data.mean():.3f}")
    print(f"Min:         {data.min():.3f}")
    print(f"Max:         {data.max():.3f}")
    print(f"Std Dev:     {data.std():.3f}")
    print(f"First value: {data[0]:.3f}")
    print(f"Last value:  {data[-1]:.3f}")


def main():
    metrics = load_metrics()

    episode_avg_queues = metrics["episode_avg_queues"]

    print("\n=== TRAINING METRICS ANALYSIS ===")

    # -------------------------------
    # Plot: Average Queue Length
    # -------------------------------
    plot_metric(
        episode_avg_queues,
        "Average Queue Length per Episode",
        "Avg Queue",
        "queue_plot.png"
    )
    print_summary("Average Queue", episode_avg_queues)

    print("\nAnalysis complete. PNG files have been saved.")


if __name__ == "__main__":
    main()
