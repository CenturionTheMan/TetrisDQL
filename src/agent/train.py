import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agent.tetris_env import TetrisEnv
from agent.agent import DQLAgent

NUM_EPISODES = 5000 # ilość gier
SAVE_EVERY = 100 # co ile zapisać model
MAX_PIECES = 500   # limit klocków na epizod — zapobiega nieskończonym grom po nauce
LEARN_EVERY = 4    # ucz się raz na N klocków zamiast przy każdym — szybszy trening
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pth")


def train():
    env = TetrisEnv() # tworzymy środowisko
    agent = DQLAgent(state_size=TetrisEnv.STATE_SIZE) # tworzymy agenta

    best_points = 0 # najwyższa ilość punktów

    for episode in range(1, NUM_EPISODES + 1):
        placements = env.reset() # tworzymy nową grę poprzez reset
        total_reward = 0.0 # łączna nagroda
        pieces_placed = 0 # ilość ułożonych klocków

        while placements and pieces_placed < MAX_PIECES: # dopóki gra istnieje i ilość obecnych klocków < niż maks
            action_idx = agent.select_action(placements) # wybieramy akcję
            state_features = placements[action_idx][2] # cechy planszy

            next_placements, reward, done = env.step(action_idx) # agent wykonuje ruch

            agent.store(state_features, reward, next_placements, done) # zapisujemy stan do bufora
            if pieces_placed % LEARN_EVERY == 0: # jeżeli jest etap na naukę to wykonujemy funkcję learn
                agent.learn()

            total_reward += reward # dodajemy nagrodę
            pieces_placed += 1 # zwiększamy ilośc klocków
            placements = next_placements # lista możliwych ruchów dla następnego

            if done:
                break

        agent.decay_epsilon() # zmniejszamy epsilon

        if episode % agent.target_update_freq == 0:
            agent.update_target() # kopiujemy wagi z policy_net do target net

        if episode % 10 == 0:
            points = env.game.get_points()
            print(
                f"Episode {episode:>5} | "
                f"Pieces: {pieces_placed:>4} | "
                f"Reward: {total_reward:>8.1f} | "
                f"Points: {points:>6} | "
                f"Epsilon: {agent.epsilon:.3f}"
            )

        points = env.game.get_points()
        if points > best_points or episode % SAVE_EVERY == 0:
            if points > best_points:
                best_points = points
            agent.save(MODEL_PATH)

    print(f"\nTraining complete. Best points: {best_points}. Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    train()
