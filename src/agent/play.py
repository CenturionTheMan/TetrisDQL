"""Run the trained DQL agent and watch it play Tetris in the console."""
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agent.tetris_env import TetrisEnv
from agent.agent import DQLAgent

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pth")
FRAME_DELAY = 0.3  # czas między klockami (placement-based: jeden krok = jeden klocek)


def play():
    env = TetrisEnv()
    agent = DQLAgent(state_size=TetrisEnv.STATE_SIZE)
    agent.load(MODEL_PATH)
    agent.epsilon = 0.0  # tryb w pełni greedy

    placements = env.reset()

    while placements and not env.game.is_game_over():
        os.system("cls" if os.name == "nt" else "clear")
        print(env.game)
        action_idx = agent.select_action(placements)
        placements, reward, done = env.step(action_idx)
        time.sleep(FRAME_DELAY)

    os.system("cls" if os.name == "nt" else "clear")
    print("=== GAME OVER ===")
    print(env.game)
    print(f"\nFinal score: {env.game.get_points()}")


if __name__ == "__main__":
    play()
