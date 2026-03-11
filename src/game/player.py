import numpy as np
from game.player_blocks import get_all_blocks
import random
from game.vec2 import Vec2
from game.grid import Grid


class Player:
    """Represents the active player-controlled Tetris block."""

    # -------------------------------------------------------------------------
    # Initialization
    # -------------------------------------------------------------------------

    def __init__(self):
        """Initialize the player and spawn the first block."""
        self.current_block: Grid = None
        self.change_block()

    # -------------------------------------------------------------------------
    # Block state
    # -------------------------------------------------------------------------

    def is_falling(self) -> bool:
        """Return True if the player currently has an active block."""
        return self.current_block is not None

    def get_block(self) -> Grid:
        """Return the current block as a Grid, or None if no block is active."""
        return self.current_block

    def get_size(self) -> Vec2:
        """Return the dimensions of the current block."""
        return self.current_block.get_shape()

    # -------------------------------------------------------------------------
    # Block management
    # -------------------------------------------------------------------------

    def change_block(self) -> None:
        """Replace the current block with a new randomly chosen one."""
        all_blocks = get_all_blocks()
        rnd = random.choice(all_blocks)
        grid = Grid(Vec2(0, 0))
        grid.set_map(rnd)
        self.current_block = grid

    def remove_block(self) -> None:
        """Clear the current block (called when it locks into the grid)."""
        self.current_block = None