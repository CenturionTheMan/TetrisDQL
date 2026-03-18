import numpy as np
from game.logic.player_blocks import get_all_blocks
import random
from game.logic.vec2 import Vec2
from game.logic.grid import Grid


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
        """Replace the current block with a new randomly chosen one.
        Each filled cell gets a random value from -1 to -10."""
        all_blocks = get_all_blocks()
        rnd = random.choice(all_blocks).copy()
        rnd[rnd != 0] = -random.randint(1, 10)
        grid = Grid(Vec2(0, 0))
        grid.set_map(rnd)
        self.current_block = grid

    def remove_block(self) -> None:
        """Clear the current block (called when it locks into the grid)."""
        self.current_block = None
    
    def set_block(self, new_block: Grid) -> None:
        self.current_block = new_block
        
    def get_rotated_block(self, is_90_positive: bool) -> Grid:
        """Rotate the current block 90 degrees in the specified direction."""
        if self.current_block is None:
            return
        
        if is_90_positive:
            new_map = np.rot90(self.current_block.get_map(), k=-1)  # clockwise
        else:
            new_map = np.rot90(self.current_block.get_map(), k=1)   # counterclockwise
            
        tmp = Grid(None)
        tmp.set_map(new_map)
        return tmp