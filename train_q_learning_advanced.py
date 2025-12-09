# train_q_learning_advanced.py
import json
import random
from collections import defaultdict
from q_learning_env_advanced import TrafficEnvAdvanced

# Q[state] = [valor_mantener, valor_cambiar]
Q = defaultdict(lambda: [0.0, 0.0])

alpha = 0.1       # learning rate
gamma = 0.97      # discount factor
epsilon = 0.15    # exploración
num_episodes = 1500
steps_per_episode = 250

def choose_action(state):
    if random.random() < epsilon:
        return random.choice([0, 1])  # explorar
    keep, switch = Q[state]
    return 0 if keep >= switch else 1

def train():
    env = TrafficEnvAdvanced()
    for episode in range(num_episodes):
        state = env.reset()
        for _ in range(steps_per_episode):
            action = choose_action(state)
            next_state, reward = env.step(action)

            best_next = max(Q[next_state])
            old_value = Q[state][action]
            Q[state][action] = old_value + alpha * (reward + gamma * best_next - old_value)

            state = next_state

        if (episode + 1) % 100 == 0:
            print(f"Episode {episode+1}/{num_episodes}")

    q_serializable = {str(k): v for k, v in Q.items()}
    with open("q_table_advanced.json", "w") as f:
        json.dump(q_serializable, f, indent=2)

    print("Training finished. Q-table saved to q_table_advanced.json")

if __name__ == "__main__":
    train()
