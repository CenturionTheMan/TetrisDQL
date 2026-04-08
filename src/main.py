from game.console_ui.console_gui import TetrisConsoleGUI
from game.logic.grid import Grid
from game.logic.vec2 import Vec2
from game.logic.tetris_handler import TetrisHandler
from game.gui.tetris_gui import TetrisGUI
import numpy as np

if __name__ == "__main__":
    grid = Grid(Vec2(10, 20))  # Example grid size (10x20)
    handler = TetrisHandler(grid)
    tetris_gui = TetrisGUI(grid, handler)
    tetris_gui.run()
    # tetrisGUI = TetrisConsoleGUI()
    # tetrisGUI.run()