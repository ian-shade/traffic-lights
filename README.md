# 🚦 Traffic Signal Control Simulation

A traffic intersection simulator comparing three intelligent control strategies: **Actuated** (rule-based), **Max-Pressure** (optimization), and **Q-Learning** (reinforcement learning).


---

## Quick Start

### Web Interface (Easiest)
Visit **https://trafficlight.ianshade.com/** to see the simulation in action.

### Run Locally

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Start the web server:**
```bash
python app.py
```
Then open `http://localhost:3003`

3. **Or run experiments:**
```bash
# Complete analysis pipeline
python run_full_analysis.py

# Multi-load experiments
python run_multiload_experiments.py
python analyze_multiload.py
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

## Project Structure

```
traffic-lights-main/
├── app.py                          # Flask server
├── simulation.py                    # Pygame simulation
├── controllers.py                   # All 3 controllers
├── train_q_learning_advanced.py    # Q-Learning training
├── q_table_advanced.json           # Trained policy
├── run_multiload_experiments.py    # Multi-load testing
├── analyze_multiload.py            # Analysis
├── web/                            # Frontend (HTML/CSS/JS)
└── results/                        # Visualizations
```

---

## Key Findings

| Traffic Load | Actuated | Max-Pressure | Q-Learning |
|--------------|----------|--------------|------------|
| Light (3.5s) | 1.14 | **1.14** ✓ | 1.14 |
| Normal (2.0s) | **1.65** ✓ | 1.33 | 2.01 |
| Heavy (1.0s) | 5.46 | **3.19** ✓ | 6.97 ❌ |

**Conclusion:** No single winner. Max-Pressure excels in extremes, Actuated wins normal traffic, Q-Learning needs diverse training.

---

## Training Q-Learning

```bash
python train_q_learning_advanced.py
```

**Config:** 3,000 episodes, α=0.2, γ=0.99, 1,458 states, 2 actions

---


## Authors
- **Karyme Nahle Acosta**
- **Ian**
- **Zaema**

---
