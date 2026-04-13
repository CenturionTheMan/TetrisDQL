"""Run the trained DQL agent and watch it play Tetris with the GUI."""
import sys
import os
import time
import pygame

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agent.tetris_env import TetrisEnv
from agent.agent import DQLAgent
from game.gui.tetris_gui import TetrisGUI

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pth")
FRAME_DELAY = 0.4  # czas między ruchami agenta (sekundy)


def play():
    env = TetrisEnv()
    agent = DQLAgent(state_size=TetrisEnv.STATE_SIZE)
    agent.load(MODEL_PATH)
    agent.epsilon = 0.0  # tryb w pełni greedy

    placements = env.reset()

    gui = TetrisGUI(env.game.get_grid(), env.game)
    gui.init_pygame()

    clock = pygame.time.Clock()
    last_step_time = time.time()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        now = time.time()
        if placements and not env.game.is_game_over() and now - last_step_time >= FRAME_DELAY:
            action_idx = agent.select_action(placements)
            placements, _reward, done = env.step(action_idx)
            last_step_time = now
            if done:
                placements = []

        gui.draw_game()

        if env.game.is_game_over():
            _draw_game_over(gui, env.game.get_points())

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


def _draw_game_over(gui: TetrisGUI, points: int):
    overlay = pygame.Surface((gui.game_width, gui.height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    gui.screen.blit(overlay, (0, 0))

    over_surf = gui.font.render("GAME OVER", True, (255, 60, 60))
    score_surf = gui.small_font.render(f"Score: {points}", True, (255, 255, 255))
    hint_surf = gui.small_font.render("Close window to exit", True, (150, 150, 150))

    cx = gui.game_width // 2
    gui.screen.blit(over_surf, over_surf.get_rect(center=(cx, gui.height // 2 - 30)))
    gui.screen.blit(score_surf, score_surf.get_rect(center=(cx, gui.height // 2 + 10)))
    gui.screen.blit(hint_surf, hint_surf.get_rect(center=(cx, gui.height // 2 + 40)))


if __name__ == "__main__":
    play()
