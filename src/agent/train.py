import sys
import os
import tqdm
from collections import deque

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agent.tetris_env import TetrisEnv
from agent.agent import DQLAgent

NUM_EPISODES = 3000 # ilość gier
SAVE_EVERY = 100 # co ile zapisać model
MAX_PIECES = 500   # limit klocków na epizod — zapobiega nieskończonym grom po nauce
MAX_PIECES_REACHED_AMT_FOR_EARLY_END = 10
LEARN_EVERY = 4    # ucz się raz na N klocków zamiast przy każdym — szybszy trening
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pth")


def train(score_algorithm: str = "SQUARE_OF_SUM", model_path: str = MODEL_PATH):
    env = TetrisEnv(score_algorithm=score_algorithm) # tworzymy środowisko
    agent = DQLAgent(state_size=TetrisEnv.STATE_SIZE) # tworzymy agenta

    best_points = 0 # najwyższa ilość punktów
    moving_avg_pieces_window = deque(maxlen=50) 
    moving_avg_points_row_window = deque(maxlen=50) 
    
    max_pieces_games = 0
    bar = tqdm.trange(1, NUM_EPISODES + 1, desc="Training", unit="episode")
    for episode in bar:
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
            
        if pieces_placed >= MAX_PIECES:
            max_pieces_games += 1
            if max_pieces_games >= MAX_PIECES_REACHED_AMT_FOR_EARLY_END:
                print(f"Early stopping at episode {episode} due to reaching max pieces limit {MAX_PIECES} for {MAX_PIECES_REACHED_AMT_FOR_EARLY_END} episodes.")
                break
        else:
            max_pieces_games = 0
            
        agent.decay_epsilon() # zmniejszamy epsilon

        if episode % agent.target_update_freq == 0:
            agent.update_target() # kopiujemy wagi z policy_net do target net

        moving_avg_pieces_window.append(pieces_placed)
        avg_pieces = sum(moving_avg_pieces_window) / len(moving_avg_pieces_window) if moving_avg_pieces_window else 0

        moving_avg_points_row_window.append(env.game.get_points_divided_by_used_blocks())
        avg_points_row = sum(moving_avg_points_row_window) / len(moving_avg_points_row_window) if moving_avg_points_row_window else 0


        bar.set_postfix({
            "AVG_PIE": f"{avg_pieces:.1f}",
            "AVG_P_ROW": f"{avg_points_row:.1f}",
            "EPS": f"{agent.epsilon:.3f}"
        })

        points = env.game.get_points()
        if points > best_points or episode % SAVE_EVERY == 0:
            if points > best_points:
                best_points = points
            agent.save(model_path)

    print(f"\nTraining complete. Best points: {best_points}. Model saved to {model_path}")


if __name__ == "__main__":
    train()
