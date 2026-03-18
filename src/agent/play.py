"""Run the trained DQL agent and watch it play Tetris in the console."""
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agent.tetris_env import TetrisEnv
from agent.dql_agent import DQLAgent

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pth")
FRAME_DELAY = 0.05  # seconds between frames


def play():
    env = TetrisEnv()
    agent = DQLAgent(
        state_size=env.state_size,
        action_size=TetrisEnv.NUM_ACTIONS,
    )
    agent.load(MODEL_PATH)
    agent.epsilon = 0.0  # no exploration, only exploit

    state = env.reset()

    while not env.game.is_game_over():
        os.system("cls" if os.name == "nt" else "clear")
        print(env.game)
        action = agent.select_action(state)
        state, reward, done = env.step(action)
        time.sleep(FRAME_DELAY)

    os.system("cls" if os.name == "nt" else "clear")
    print("=== GAME OVER ===")
    print(env.game)
    print(f"\nFinal score: {env.game.get_points()}")


if __name__ == "__main__":
    play()
