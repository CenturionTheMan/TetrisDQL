import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agent.train import train

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model_sum_of_square.pth")

if __name__ == "__main__":
    train(score_algorithm="SUM_OF_SQUARE", model_path=MODEL_PATH)
