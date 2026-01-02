# Experiment Workflow

## Quick Start (Normal Traffic)

Generate metrics for all 5 controllers at normal traffic load:

```bash
python generate_metrics.py
```

This creates 5 CSV files in `metrics/` folder (~2 minutes runtime).

Then analyze and visualize:

```bash
python compare_results.py
```

Results saved to `results/` folder with comprehensive plots and CSV summaries.

---

## Full Multi-Load Experiment

Run all controllers at 3 different traffic loads (light/normal/heavy):

```bash
python run_multiload_experiments.py
```

This creates 15 CSV files in `metrics/` folder (~5 minutes runtime).

Then analyze across loads:

```bash
python analyze_multiload.py
```

Results saved to `results/multiload/` with comparison plots.

---

## Interactive Simulation (Optional)

For manual testing and visualization:

```bash
python simulation.py
```

Controls:
- `1-5` - Switch controller
- `UP/DOWN` - Adjust spawn rate
- `M` - Export current metrics
- `R` - Reset

---

## Output Structure

```
metrics/
├── metrics_fixed_time.csv
├── metrics_actuated.csv
├── metrics_max_pressure.csv
├── metrics_fuzzy.csv
├── metrics_q_learning.csv
├── metrics_*_light.csv      (if multiload was run)
├── metrics_*_normal.csv
└── metrics_*_heavy.csv

results/
├── comparison_summary.csv
├── direction_fairness.csv
├── bar_comparison.png
├── total_queue_time.png
├── switches_over_time.png
├── cumulative_queue.png
├── queue_distributions.png
├── queue_boxplots.png
├── direction_fairness.png
├── direction_*.png
├── avg_wait_time.png
└── multiload/
    ├── multiload_summary.csv
    ├── multiload_comparison.png
    └── *_loads.png
```

---

## Recommended Order for Paper

1. Run `python generate_metrics.py` - Get baseline results
2. Run `python compare_results.py` - Generate standard plots
3. Run `python run_multiload_experiments.py` - Full experiment
4. Run `python analyze_multiload.py` - Multi-load analysis
5. Use plots from `results/` in your paper
