# 🚦 Traffic Signal Control Simulation

A traffic intersection simulator comparing three intelligent control strategies: **Actuated** (rule-based), **Max-Pressure** (optimization), and **Q-Learning** (reinforcement learning).

---

## Quick Start

### Web Interface (Easiest)
Visit **https://trafficlight.ianshade.com/** to see the simulation in action.

### Run Locally

1. **Create virtual environment and install dependencies:**
```bash
python3 -m venv env/python
source env/python/bin/activate
python3 -m pip install -r requirements.txt
```

2. **Start the web server:**
```bash
python3 app.py
```
Then open **http://localhost:3003**

3. **Or run analysis:**
```bash
# Complete analysis pipeline
python3 run_full_analysis.py

# Multi-load experiments
python3 run_multiload_experiments.py
python3 analyze_multiload.py
```

---

## Requirements

```txt
flask>=2.3.0
flask-socketio>=5.3.0
flask-cors>=4.0.0
python-socketio>=5.9.0
pygame>=2.5.0
pandas>=2.0.0
matplotlib>=3.7.0
numpy>=1.24.0
gunicorn>=21.2.0
eventlet>=0.33.3
```

---

## Controllers

### 1. Actuated (Rule-Based)
- Uses threshold logic: switches when opposing queue > 6 vehicles
- Best for: Normal traffic (1.65 avg queue)

### 2. Max-Pressure (Optimization)
- Calculates pressure differentials between directions
- Best for: Extreme conditions (heavy: 3.19) and fairness (0.101 variance)

### 3. Q-Learning (Reinforcement Learning)
- Trained agent with 1,458 state space over 3,000 episodes
- Training: α=0.2, γ=0.99, ε=0.3→0.05
- Best for: Normal traffic efficiency, but fails in heavy traffic (6.97)

---


## Training Q-Learning

```bash
python3 train_q_learning_advanced.py
```

---


## Authors
- Zaema Dar
- Karyme Nahle Acosta
- Ihsan Abourshaid

---
