# Traffic Intersection Simulation with Q-Learning

This project implements a smart traffic‑light controller using **Q-Learning** together with a full **graphical simulation** built in Pygame. The system simulates a 4‑way intersection (North, South, East, West) where cars randomly arrive and the traffic‑light agent learns when to keep the current light phase or switch phases to manage congestion more efficiently.

---

## 📁 Project Structure

```
/project
│
├── simulation.py                # Full visual Pygame simulation
├── car_manager.py               # Car spawning, movement & VIP logic
├── traffic_controller.py        # Rule-based controller for simulation mode
├── models.py                    # Data classes & enums
│
├── q_learning_env_advanced.py   # Training environment for RL
├── train_q_learning_advanced.py # Q-learning training loop (updated rewards & metrics)
├── q_table_advanced.json        # Learned Q-table saved after training
│
├── training_metrics.json        # Reward, queue, and switch metrics from training
├── analysis.py                  # Generates graphs from RL training performance
│
├── reward_plot.png              # RL reward curve
├── queue_plot.png               # Average queue size per episode
├── switch_plot.png              # Phase switching metrics
│
└── README.md                    # Project documentation
```

---

## 🚦 Project Overview

The goal is to create a realistic traffic-light system capable of adapting to real‑time congestion. The project has two major components:

### ⭐ **1. Reinforcement Learning (Q-Learning) Agent**
The agent learns when to **keep** or **switch** the green light between:
- **NS (North–South)**
- **EW (East–West)**

State features include:
- Discretized queue lengths (N, S, E, W)
- Current light phase
- Duration of current green phase
- Traffic imbalance between axes

Rewards encourage:
- Reducing queues  
- Avoiding excessive switching  
- Preventing extreme congestion  

After training, the agent’s learned values are stored in `q_table_advanced.json`.

---

### ⭐ **2. Visual Traffic Simulator (Pygame)**

`simulation.py` displays a full intersection:
- Cars spawn from all directions with realistic spacing  
- **VIP vehicles** (ambulances, police, firefighters) get automatic green‑light priority  
- Smooth movement and lane-based positioning  
- Realistic yellow/green/red timing  
- A control panel showing queue counts and timers  

The simulation currently uses a **rule-based** traffic controller, not the RL agent. Integrating RL into the live simulation is suggested future work.

---

## 📊 Reinforcement Learning Metrics

Running:

```
python train_q_learning_advanced.py
```

produces:
- `training_metrics.json`
- `reward_plot.png`
- `queue_plot.png`
- `switch_plot.png`

You can analyze them with:

```
python analysis.py
```

### Example Conclusions
- Rewards improve significantly over training (from ~–300 to ~–230).  
- Average queues decrease and stabilize.  
- Phase switching becomes less erratic and more consistent.  

These results show that the agent is learning a more efficient and stable traffic‑light policy.

---

## ▶️ How to Run the Simulation

### 1. Install dependencies
```
pip install pygame matplotlib
```

### 2. Run the visual simulation
```
python simulation.py
```

Controls:
- **UP/DOWN** → change spawn rate  
- **R** → reset simulation  

VIP cars automatically trigger green-light priority.

---

## ▶️ How to Train the Q-Learning Model

```
python train_q_learning_advanced.py
```
---
