from typing import Tuple
import numpy as np
from game.logic.player import Player
from game.logic.vec2 import Vec2, VEC_DOWN, VEC_LEFT, VEC_RIGHT, VEC_UP
from game.logic.grid import Grid
import random


class TetrisHandler(object):
    """Main game logic handler for Tetris. Manages the grid, player block, 
    collision detection, row clearing, and scoring."""

    # -------------------------------------------------------------------------
    # Initialization
    # -------------------------------------------------------------------------

    def __init__(self, gird_size: Tuple[int, int] = (10, 20)):
        """
            Set up the grid, player, and initial game state.
            gird_size: (width, height) tuple specifying the grid dimensions.
        """
        self.__grid = Grid(Vec2(gird_size[0], gird_size[1]))
        self.__player = Player()

        player_height = self.__player.get_size().get_y()
        self.__player_top_left = Vec2(0, -player_height)  # Spawn position (above grid)
        self.__points = 0
        self.__is_end = False

    # -------------------------------------------------------------------------
    # Game loop
    # -------------------------------------------------------------------------

    def update(self) -> None:
        """Advance the game by one tick. Handles falling, collision, row clearing,
        end condition, and spawning the next block."""
        if self.__is_end:
            return

        if self.__player.is_falling():
            if self.has_player_collided():
                # Lock the block into the grid and clear the player
                self.add_player_shape_to_grid()
                self.__player.remove_block()
            else:
                # Move the block one step down
                self.__player_top_left += VEC_DOWN
        else:
            # Block just landed - clear full rows, check end, spawn next block
            _ = self.check_rows_fulfillment()

            if self.check_end_condition():
                return

            self.create_player_block()

    # -------------------------------------------------------------------------
    # Game state
    # -------------------------------------------------------------------------

    def is_game_over(self) -> bool:
        """Return True if the game has ended."""
        return self.__is_end

    def get_points(self) -> int:
        """Return the current score (one point per cleared row)."""
        return self.__points

    def check_end_condition(self) -> bool:
        """Check if any cell in the top row is occupied. If so, end the game."""
        for x in range(self.__grid.get_shape().get_x()):
            if self.__grid.get_value(x, 0) != 0:
                self.__is_end = True
                return True
        return False

    # -------------------------------------------------------------------------
    # Player management
    # -------------------------------------------------------------------------

    def create_player_block(self) -> None:
        """Spawn a new random block at a random x position above the grid.
        Does nothing if a block is already active."""
        if self.__player.get_block() is not None:
            return
        self.__player.change_block()
        self.__player_top_left = Vec2(
            random.randint(0, self.__grid.get_shape().get_x() - self.__player.get_size().get_x()),
            -self.__player.get_size().get_y()
        )

    def add_player_shape_to_grid(self) -> None:
        """Write the current player block's values into the permanent grid."""
        block = self.__player.get_block()
        shape = block.get_shape()
        pbl = self.__player_top_left

        for x in range(shape.get_x()):
            for y in range(shape.get_y()):
                v = block.get_value(x, y)
                if v != 0:
                    self.__grid.set_value(pbl.get_x() + x, pbl.get_y() + y, -v)

    def try_move(self, is_right : bool) -> bool:
        """Attempt to move the player block left or right. Does nothing if the move would cause a collision."""
        if self.__is_end or not self.__player.is_falling():
            return
        
        dir_change = VEC_RIGHT if is_right else VEC_LEFT
        
        tmp_player_pos = self.__player_top_left + dir_change 
        if not self.__grid.is_gird_overlap(self.__player.get_block(), tmp_player_pos):
            self.__player_top_left = tmp_player_pos
            return True
        return False
        
    def try_rotate(self, is_clockwise: bool) -> bool:
        """
        Attempt to rotate the player block 90 or -90 degrees.
        Does nothing if the rotation would cause a collision.
        """
        if self.__is_end or not self.__player.is_falling():
            return
        
        new_block = self.__player.get_rotated_block(is_clockwise)
        if not self.__grid.is_gird_overlap(new_block, self.__player_top_left):
            self.__player.set_block(new_block)
            return True
        return False
            
    # -------------------------------------------------------------------------
    # Collision detection
    # -------------------------------------------------------------------------

    def has_player_collided(self) -> bool:
        """Return True if the player block would collide on the next frame -
        either by hitting the bottom of the grid or landing on a placed block."""
        ptl = self.__player_top_left
        block = self.__player.get_block()
        shape = block.get_shape()

        for xp in range(shape.get_x()):
            for yp in range(shape.get_y()):
                val = block.get_value(xp, yp)
                if val == 0:
                    continue  # Empty cell in the block shape, skip

                y_tmp = yp + ptl.get_y()
                if y_tmp < 0:
                    continue  # This pixel is still above the visible grid

                x_g, y_g = ptl.get_x() + xp, y_tmp + 1

                if not self.__grid.is_pos_in_bounds(Vec2(x_g, y_g)):
                    return True  # Next position would be out of bounds (hit bottom)

                if self.__grid.get_value(x_g, y_g) != 0:
                    return True  # Next position is occupied by a placed block

        return False

    # -------------------------------------------------------------------------
    # Row clearing
    # -------------------------------------------------------------------------

    def check_rows_fulfillment(self) -> bool:
        """Find and clear all fully filled rows, then shift everything above down.
        Awards one point per cleared row. Returns True if any rows were cleared."""
        to_remove = []
        for row_idx in range(self.__grid.get_shape().get_y()):
            if not self.__grid.check_if_row_has_any_zeros(row_idx):
                to_remove.append(row_idx)

        if len(to_remove) == 0:
            return False

        self.__points += len(to_remove)

        # Shift all rows above each cleared row downward
        for row_idx in to_remove:
            for y in range(row_idx, 0, -1):
                for x in range(self.__grid.get_shape().get_x()):
                    self.__grid.set_value(x, y, self.__grid.get_value(x, y - 1))

        return True

    # -------------------------------------------------------------------------
    # Rendering
    # -------------------------------------------------------------------------

    def get_draw_grid(self) -> Grid:
        """Return a copy of the grid with the active player block overlaid.
        Safe to use for rendering without modifying the actual game state."""
        tmp_grid = self.__grid.copy()

        if self.__player.get_block() is None:
            return tmp_grid

        block = self.__player.get_block()
        shape = block.get_shape()
        pbl = self.__player_top_left

        for x in range(shape.get_x()):
            for y in range(shape.get_y()):
                v = block.get_value(x, y)
                if v != 0:
                    px, py = pbl.get_x() + x, pbl.get_y() + y
                    _ = tmp_grid.try_set_value(px, py, v)

        return tmp_grid
    
    def __str__(self) -> str:
        """Return a formatted string showing the current game state:
        the live grid (with active block overlaid), score, and game over status."""
        status = "GAME OVER" if self.__is_end else "PLAYING"
        header = f"Status: {status}  |  Points: {self.__points}"
        separator = "-" * len(header)
        return f"{header}\n{separator}\n{self.get_draw_grid()}"