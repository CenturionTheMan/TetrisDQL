import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agent.train import train

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model_constant.pth")

if __name__ == "__main__":
    train(score_algorithm="CONSTANT", model_path=MODEL_PATH)
