# train_q_learning_advanced.py
#
# This script trains a Q-learning agent to control a traffic light.
# The agent learns when to keep the current phase and when to switch,
# based on the state provided by the environment (traffic queues, timing, etc.).
#
# It also records simple performance metrics per episode:
# - total reward
# - average total queue
# - number of phase switches

import json
import random
from collections import defaultdict
from q_learning_env_advanced import TrafficEnvAdvanced

# Q-table structure:
# Q[state] = [value_if_keep_phase, value_if_switch_phase]
Q = defaultdict(lambda: [0.0, 0.0])

# Hyperparameters for Q-learning
alpha = 0.2        # learning rate (slightly higher to learn faster)
gamma = 0.99       # discount factor (more focus on long-term rewards)
epsilon = 0.3      # initial exploration probability
epsilon_min = 0.05 # minimum exploration
epsilon_decay = 0.995  # decay per episode

num_episodes = 3000
steps_per_episode = 250


def choose_action(state):
    """
    Chooses an action using epsilon-greedy.
    Action:
        0 = keep current traffic light phase
        1 = switch to the other phase
    """
    # With probability epsilon: pick a random action
    if random.random() < epsilon:
        return random.choice([0, 1])

    # Otherwise pick the best known action
    keep, switch = Q[state]
    return 0 if keep >= switch else 1


def train():
    """
    Main training loop.
    The agent interacts with the environment, updates the Q-table,
    and collects basic performance metrics per episode.
    """
    global epsilon  # to update with decay

    env = TrafficEnvAdvanced()

    # Metrics storage
    episode_rewards = []        # total reward per episode
    episode_avg_queues = []     # average total queue per episode
    episode_switches = []       # number of phase switches per episode

    for episode in range(num_episodes):
        state = env.reset()   # start a new episode
        total_reward = 0.0

        for _ in range(steps_per_episode):
            action = choose_action(state)

            # Apply the action in the environment
            next_state, reward = env.step(action)
            total_reward += reward

            # Q-learning update rule
            best_next = max(Q[next_state])        # best predicted future value
            old_value = Q[state][action]          # current Q-value

            # Update the Q-value
            Q[state][action] = old_value + alpha * (
                reward + gamma * best_next - old_value
            )

            # Move to the next state
            state = next_state

        # Compute metrics for this episode
        if env.total_steps > 0:
            avg_queue = env.total_queue_sum / env.total_steps
        else:
            avg_queue = 0.0

        episode_rewards.append(total_reward)
        episode_avg_queues.append(avg_queue)
        episode_switches.append(env.switches_this_episode)

        # Epsilon decay: explore a lot at the beginning, less later
        epsilon = max(epsilon_min, epsilon * epsilon_decay)

        # Display progress every 200 episodes
        if (episode + 1) % 200 == 0:
            print(
                f"Episode {episode + 1}/{num_episodes} | "
                f"Total reward: {total_reward:.2f} | "
                f"Avg queue: {avg_queue:.2f} | "
                f"Switches: {env.switches_this_episode} | "
                f"Epsilon: {epsilon:.3f}"
            )

    # Convert keys to strings before saving (JSON doesn't allow tuple keys)
    q_serializable = {str(k): v for k, v in Q.items()}

    # Save trained Q-table
    with open("q_table_advanced.json", "w") as f:
        json.dump(q_serializable, f, indent=2)

    print("Training finished. Q-table saved to q_table_advanced.json")

    # Save training metrics for later analysis
    metrics = {
        "episode_rewards": episode_rewards,
        "episode_avg_queues": episode_avg_queues,
        "episode_switches": episode_switches,
        "alpha": alpha,
        "gamma": gamma,
        "epsilon_final": epsilon,
        "epsilon_min": epsilon_min,
        "epsilon_decay": epsilon_decay,
        "num_episodes": num_episodes,
        "steps_per_episode": steps_per_episode,
    }
    with open("training_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print("Training metrics saved to training_metrics.json")


if __name__ == "__main__":
    train()
