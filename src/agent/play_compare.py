import sys
import os
import time
import pygame
import random
import numpy as np
import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agent.tetris_env import TetrisEnv
from agent.agent import DQLAgent
from game.gui.tetris_gui import TetrisGUI

MODEL_SQUARE   = os.path.join(os.path.dirname(__file__), "model_sum_of_square.pth")
MODEL_CONSTANT = os.path.join(os.path.dirname(__file__), "model_constant.pth")
FRAME_DELAY  = .1
LABEL_HEIGHT = 40
CELL_SIZE    = 35


def _make(model_path: str) -> tuple:
    env = TetrisEnv(score_algorithm="SUM_OF_SQUARE")
    agent = DQLAgent(state_size=TetrisEnv.STATE_SIZE)
    agent.load(model_path)
    agent.epsilon = 0.0
    placements = env.reset()
    return env, agent, placements


def _draw_game_over(surface: pygame.Surface, font, small_font, points: int) -> None:
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))
    cx, cy = surface.get_width() // 2, surface.get_height() // 2
    surface.blit(font.render("GAME OVER", True, (255, 60, 60)),
                 font.render("GAME OVER", True, (255, 60, 60)).get_rect(center=(cx, cy - 20)))
    surface.blit(small_font.render(f"Score: {points}", True, (255, 255, 255)),
                 small_font.render(f"Score: {points}", True, (255, 255, 255)).get_rect(center=(cx, cy + 15)))


def play() -> None:
    pygame.init()

    panel_w = TetrisEnv.GRID_WIDTH * CELL_SIZE + 200
    game_h  = TetrisEnv.GRID_HEIGHT * CELL_SIZE
    divider = 4
    total_w = panel_w * 2 + divider
    total_h = LABEL_HEIGHT + game_h

    screen = pygame.display.set_mode((total_w, total_h))
    pygame.display.set_caption("Tetris DQL — Square vs Constant")

    label_font = pygame.font.SysFont("Segoe UI", 22, bold=True)
    big_font   = pygame.font.SysFont("Segoe UI", 28, bold=True)
    small_font = pygame.font.SysFont("Segoe UI", 18)

    sub_left  = screen.subsurface(pygame.Rect(0,              LABEL_HEIGHT, panel_w, game_h))
    sub_right = screen.subsurface(pygame.Rect(panel_w + divider, LABEL_HEIGHT, panel_w, game_h))

    env_sq, agent_sq, placements_sq = _make(MODEL_SQUARE)
    env_ct, agent_ct, placements_ct = _make(MODEL_CONSTANT)

    def make_gui(env, sub):
        gui = TetrisGUI(env.game.get_grid(), env.game, cell_size=CELL_SIZE)
        gui.screen     = sub
        gui.font       = big_font
        gui.small_font = small_font
        return gui

    gui_sq = make_gui(env_sq, sub_left)
    gui_ct = make_gui(env_ct, sub_right)

    clock     = pygame.time.Clock()
    last_step = time.time()
    done_sq   = False
    done_ct   = False
    running   = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        now = time.time()
        if now - last_step >= FRAME_DELAY:
            if placements_sq and not done_sq:
                idx = agent_sq.select_action(placements_sq)
                placements_sq, _, done_sq = env_sq.step(idx)

            if placements_ct and not done_ct:
                idx = agent_ct.select_action(placements_ct)
                placements_ct, _, done_ct = env_ct.step(idx)

            last_step = now

        screen.fill((15, 15, 15))
        pygame.draw.line(screen, (80, 80, 80),
                         (panel_w + divider // 2, 0),
                         (panel_w + divider // 2, total_h), divider)

        # --- labels ---
        lbl_sq = label_font.render("SQUARE MODEL", True, (255, 200, 50))
        lbl_ct = label_font.render("CONSTANT MODEL", True, (100, 180, 255))
        screen.blit(lbl_sq, lbl_sq.get_rect(center=(panel_w // 2, LABEL_HEIGHT // 2)))
        screen.blit(lbl_ct, lbl_ct.get_rect(center=(panel_w + divider + panel_w // 2, LABEL_HEIGHT // 2)))

        # --- games ---
        gui_sq.draw_game()
        gui_ct.draw_game()

        if done_sq or env_sq.game.is_game_over():
            _draw_game_over(sub_left, big_font, small_font, env_sq.game.get_points())
        if done_ct or env_ct.game.is_game_over():
            _draw_game_over(sub_right, big_font, small_font, env_ct.game.get_points())

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    seed = 42

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    # torch.use_deterministic_algorithms(True)
    
    play()
