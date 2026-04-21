from game.console_ui.console_gui import TetrisConsoleGUI
from game.logic.tetris_handler import TetrisHandler
from game.gui.tetris_gui import TetrisGUI
import numpy as np

if __name__ == "__main__":
    handler = TetrisHandler(score_algorithm="SUM_OF_SQUARE", gird_size=(10, 20))
    tetris_gui = TetrisGUI(handler.get_grid(), handler)
    tetris_gui.run()
