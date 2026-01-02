# 🚦 Intelligent Traffic Light Control Simulation

## Overview
This project implements a four-way traffic intersection simulator with multiple intelligent traffic signal control strategies. The objective is to evaluate different decision-making approaches under uncertain traffic demand and compare their effectiveness in reducing congestion and queue lengths.

The simulation models a realistic urban intersection with North, South, East, and West approaches, enforcing minimum green times, yellow phases, and stochastic vehicle arrivals. Several control strategies are implemented and evaluated under identical conditions.

This project was developed as part of an academic assessment focused on knowledge-based systems and decision-making under uncertainty.

---

## Implemented Controllers
The simulator supports five traffic signal control strategies:

1. **Fixed-Time Control**  
   Uses a predefined signal cycle, independent of traffic conditions.

2. **Actuated Control (Rule-Based)**  
   Extends or switches phases based on observed queue lengths, subject to timing constraints.

3. **Max-Pressure Control**  
   Selects phases based on queue imbalance between competing directions.

4. **Fuzzy Logic Control**  
   Uses fuzzy membership functions and heuristic rules to prioritise phases with higher congestion.

5. **Q-Learning (Reinforcement Learning)**  
   A tabular Q-learning agent that learns when to switch phases based on a discretised state representation of queues and signal timing.

---

## Simulation Features
- Four-way intersection (N, S, E, W)
- Realistic traffic light phases (green, yellow, red)
- Minimum green time enforcement
- Stochastic vehicle spawning
- Optional VIP vehicle tracking
- Real-time visualisation using Pygame
- Metric logging and CSV export for offline analysis

---

## Quick Start

Generate metrics for all controllers and analyze results:

```bash
python generate_metrics.py
python compare_results.py
```

For comprehensive multi-load experiments:

```bash
python run_multiload_experiments.py
python analyze_multiload.py
```

Or run everything at once:

```bash
python run_full_analysis.py
```

See [WORKFLOW.md](WORKFLOW.md) for detailed instructions.

---

## Project Structure
```text
traffic-lights/
│
├── traffic_sim.py
├── car_manager.py
├── traffic_light.py
├── controllers/
│   ├── fixed_time.py
│   ├── actuated.py
│   ├── max_pressure.py
│   ├── fuzzy_controller.py
│   └── q_learning_controller.py
│
├── train_q_learning_advanced.py
├── q_table_advanced.json
│
├── metrics/
│   ├── metrics_fixed.csv
│   ├── metrics_actuated.csv
│   ├── metrics_max_pressure.csv
│   ├── metrics_fuzzy.csv
│   └── metrics_q_learning.csv
│
├── compare_results.py
├── comparison_summary.csv
│
├── plots/
│   ├── reward_plot.png
│   ├── queue_plot.png
│   ├── switch_plot.png
│   ├── comparison_plot_total_queue.png
│   └── comparison_plot_vip_queue.png
│
└── README.md
```

---

## Requirements
- Python 3.9+
- Pygame
- NumPy
- Pandas
- Matplotlib

Install dependencies:
```bash
pip install pygame numpy pandas matplotlib
```

---

## Interactive Simulation (Optional)

For visual demonstration and manual testing:

```bash
python simulation.py
```

### Keyboard Controls
- `1` – Fixed-time controller
- `2` – Actuated controller
- `3` – Max-pressure controller
- `4` – Fuzzy logic controller
- `5` – Q-learning controller
- `↑ / ↓` – Increase or decrease vehicle spawn rate
- `R` – Reset simulation
- `M` – Export current metrics  

---

## Training the Q-Learning Agent
```bash
python train_q_learning_advanced.py
```

This script trains a tabular Q-learning agent through repeated simulation episodes.  
The learned policy is stored in `q_table_advanced.json`.  
Training metrics such as cumulative reward, average queue length, and switching behaviour are logged and visualised.

---

## Evaluation and Metrics

Generate comprehensive metrics for all controllers:

```bash
python generate_metrics.py
python compare_results.py
```

Collected metrics include:
- Total queue length
- Per-direction queue lengths (North, South, East, West)
- VIP queue counts
- Phase switches
- Average wait time per car

Analysis outputs:
- Performance comparison tables (CSV)
- Bar charts comparing controllers
- Queue length time series
- Phase switch behavior
- Cumulative congestion burden
- Distribution plots (histograms, box plots)
- Per-direction fairness analysis
- Average wait time comparison

---
## Experimental Setup

All controllers are evaluated under identical conditions to ensure fair comparison.

### Standard Evaluation
```bash
python generate_metrics.py
```
Runs all 5 controllers for 120 seconds at normal traffic load (spawn_rate=2.0s).

### Multi-Load Testing
```bash
python run_multiload_experiments.py
```
Evaluates all controllers under three traffic scenarios:
- **Light traffic** (spawn_rate=3.5s): Low congestion, tests efficiency
- **Normal traffic** (spawn_rate=2.0s): Typical urban conditions
- **Heavy traffic** (spawn_rate=1.0s): High demand, stress test

Each run is 120 seconds with identical signal timing constraints and randomization.

---

## Authors
- **Karyme Nahle Acosta**
- **Ian**
- **Zaema**

---