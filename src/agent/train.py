import sys
import os

# Add src/ to path so imports work when running from src/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agent.tetris_env import TetrisEnv
from agent.dql_agent import DQLAgent

NUM_EPISODES = 2000
MAX_STEPS_PER_EPISODE = 5000
SAVE_EVERY = 100
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pth")


def train():
    env = TetrisEnv()
    agent = DQLAgent(
        state_size=env.state_size,
        action_size=TetrisEnv.NUM_ACTIONS,
    )

    best_reward = float("-inf")

    for episode in range(1, NUM_EPISODES + 1):
        state = env.reset()
        total_reward = 0.0
        steps = 0

        for step in range(MAX_STEPS_PER_EPISODE):
            action = agent.select_action(state)
            next_state, reward, done = env.step(action)

            agent.store(state, action, reward, next_state, done)
            agent.learn()

            state = next_state
            total_reward += reward
            steps += 1

            if done:
                break

        agent.decay_epsilon()

        # Update target network periodically
        if episode % agent.target_update_freq == 0:
            agent.update_target()

        # Logging
        if episode % 10 == 0:
            print(
                f"Episode {episode:>5} | "
                f"Steps: {steps:>5} | "
                f"Reward: {total_reward:>8.1f} | "
                f"Points: {env.game.get_points():>6} | "
                f"Epsilon: {agent.epsilon:.3f}"
            )

        # Save best model
        if total_reward > best_reward:
            best_reward = total_reward
            agent.save(MODEL_PATH)

        # Periodic save
        if episode % SAVE_EVERY == 0:
            agent.save(MODEL_PATH)

    print(f"\nTraining complete. Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    train()
