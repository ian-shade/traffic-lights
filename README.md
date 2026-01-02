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

## Running the Simulation
```bash
python traffic_sim.py
```

### Keyboard Controls
- `1` – Fixed-time controller  
- `2` – Actuated controller  
- `3` – Max-pressure controller  
- `4` – Fuzzy logic controller  
- `5` – Q-learning controller  
- `↑ / ↓` – Increase or decrease vehicle spawn rate  
- `R` – Reset simulation  
- `M` – Export metrics to CSV  

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
During simulation, the following metrics are collected:
- Total queue length
- Per-direction queue lengths (North, South, East, West)
- VIP queue indicator
- Number of phase switches
- Simulation time

Metrics are exported as CSV files and analysed using:
```bash
python compare_results.py
```

This script generates:
- Aggregated performance tables
- Queue comparison plots across controllers
- VIP queue visualisations

---
## Experimental Setup
Each controller is evaluated across three simulation runs under identical signal timing constraints:

- A 2-minute simulation with the default vehicle spawn rate  
- A 5-minute simulation to evaluate performance under sustained traffic conditions  
- A 2-minute simulation with a reduced vehicle spawn rate (0.5) to assess controller behaviour under lighter demand  

All controllers operate under the same signal timing parameters and vehicle arrival processes within each run, ensuring a fair and consistent comparison across control strategies.

---

## Authors
- **Karyme Nahle Acosta**
- **Ihsan Abourshaid**
- **Zaema Dar**

---