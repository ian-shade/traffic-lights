# train_q_learning.py
import json
import random
from collections import defaultdict
from q_learning_env import TrafficEnv

# Q[state] = [valor_mantener, valor_cambiar]
Q = defaultdict(lambda: [0.0, 0.0])

alpha = 0.1      # learning rate
gamma = 0.95     # discount
epsilon = 0.1    # exploración
num_episodes = 1000
steps_per_episode = 200

def choose_action(state):
    if random.random() < epsilon:
        return random.choice([0, 1])  # explorar
    keep, switch = Q[state]
    return 0 if keep >= switch else 1

def train():
    env = TrafficEnv()
    for episode in range(num_episodes):
        state = env.reset()
        for _ in range(steps_per_episode):
            action = choose_action(state)
            next_state, reward = env.step(action)

            best_next = max(Q[next_state])
            old_value = Q[state][action]
            Q[state][action] = old_value + alpha * (reward + gamma * best_next - old_value)

            state = next_state

    # Guardar tabla Q
    q_serializable = {str(k): v for k, v in Q.items()}
    with open("q_table.json", "w") as f:
        json.dump(q_serializable, f, indent=2)

    print("Training finished. Q-table saved to q_table.json")

if __name__ == "__main__":
    train()
