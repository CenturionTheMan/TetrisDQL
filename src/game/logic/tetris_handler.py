from typing import Literal, Tuple
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

    def __init__(self, score_algorithm: Literal["SUM_OF_SQUARE", "CONSTANT"], gird_size: Tuple[int, int] = (10, 20)):
        """
            Set up the grid, player, and initial game state.
            gird_size: (width, height) tuple specifying the grid dimensions.
        """
        self.__blocks_used_count = 1
        
        if score_algorithm not in ["SUM_OF_SQUARE", "CONSTANT"]:
            raise ValueError(f"Invalid score algorithm: {score_algorithm}. Must be 'SUM_OF_SQUARE' or 'CONSTANT'.")
        
        self.__score_algh: Literal["SUM_OF_SQUARE", "CONSTANT"] = score_algorithm
        self.__grid = Grid(Vec2(gird_size[0], gird_size[1]))
        self.__player = Player()

        player_height = self.__player.get_size().get_y()
        self.__player_top_left = Vec2(0, -player_height)  # Spawn position (above grid)
        self.__points = 0
        self.__is_end = False
        self.create_player_block()

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
            self.__blocks_used_count += 1
            

    # -------------------------------------------------------------------------
    # Game state
    # -------------------------------------------------------------------------

    def is_game_over(self) -> bool:
        """Return True if the game has ended."""
        return self.__is_end

    def get_points(self) -> int:
        """Return the current score."""
        return self.__points
    
    def get_points_divided_by_used_blocks(self) -> float:
        """Return the current score."""
        return self.__points / self.__blocks_used_count

    def get_grid(self) -> Grid:
        """Return the internal grid (without the active block)."""
        return self.__grid

    def get_player_top_left(self) -> Vec2:
        """Return the top-left position of the active player block."""
        return self.__player_top_left

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
        if self.__player.get_block() is not None:
            return

        # Generujemy nasz nowy, "punktowy" klocek
        new_block = self.generate_random_piece()

        # Ustawiamy go w obiekcie gracza
        self.__player.set_block(new_block)

        # Reszta Twojej logiki pozycjonowania
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
                    self.__grid.try_set_value(pbl.get_x() + x, pbl.get_y() + y, -v)

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

    def get_player_block(self):
        """Return the current player block grid (None if no block is active)."""
        return self.__player.get_block()

    def execute_placement(self, rotations: int, target_col: int) -> int:
        """Rotate piece clockwise `rotations` times, teleport to target_col, hard-drop.

        Returns the number of lines cleared by the placement.
        Spawns the next piece automatically (or marks game over).
        """
        # Rotate clockwise N times
        for _ in range(rotations % 4):
            new_block = self.__player.get_rotated_block(is_90_positive=True)
            self.__player.set_block(new_block)

        # Teleport horizontally to target column (keep spawn y)
        self.__player_top_left = Vec2(target_col, self.__player_top_left.get_y())

        # Hard drop
        while not self.has_player_collided():
            self.__player_top_left += VEC_DOWN

        # Lock into grid
        self.add_player_shape_to_grid()
        self.__player.remove_block()

        # Clear lines and count
        lines_cleared = self.check_rows_fulfillment()

        # Check end condition; spawn next piece if game continues
        if not self.check_end_condition():
            self.create_player_block()

        return lines_cleared

    def check_rows_fulfillment(self) -> int:
        """Find and clear all fully filled rows, then shift everything above down.
        Awards points per sum squared of cleared row squares. Returns the number of rows cleared."""
        to_remove = []
        for row_idx in range(self.__grid.get_shape().get_y()):
            if not self.__grid.check_if_row_has_any_zeros(row_idx):
                to_remove.append(row_idx)

        if len(to_remove) == 0:
            return 0

        for row_idx in to_remove:
            if self.__score_algh == "SUM_OF_SQUARE":   
                row_sum = 0
                for x in range(self.__grid.get_shape().get_x()):
                    row_sum += self.__grid.get_value(x, row_idx) 
                self.__points += row_sum ** 2
            elif self.__score_algh == "CONSTANT":
                self.__points += 1
            else:
                raise ValueError(f"Unknown score algorithm: {self.__score_algh}")
            
        # Shift all rows above downward
        for row_idx in to_remove:
            for y in range(row_idx, 0, -1):
                for x in range(self.__grid.get_shape().get_x()):
                    self.__grid.set_value(x, y, self.__grid.get_value(x, y - 1))
            for x in range(self.__grid.get_shape().get_x()):
                self.__grid.set_value(x, 0, 0)

        return len(to_remove)

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

    def generate_random_piece(self) -> Grid:
        # Definicje klasycznych kształtów
        shapes = [
            np.array([[1, 1, 1], [0, 1, 0]]),  # T
            np.array([[1, 1], [1, 1]]),  # Square
            np.array([[1, 1, 1, 1]]),  # Line
            np.array([[1, 1, 0], [0, 1, 1]]),  # Z
            np.array([[0, 1, 1], [1, 1, 0]]),  # S
            np.array([[1, 0, 0], [1, 1, 1]]),  # L
            np.array([[0, 0, 1], [1, 1, 1]])  # J
        ]
        shape = random.choice(shapes)

        # Tworzymy tablicę o tym samym kształcie, ale z losowymi liczbami 1-9
        # Tam gdzie w 'shape' jest 1, wstawiamy losową cyfrę. Tam gdzie 0, zostaje 0.
        random_values = np.random.randint(1, 10, size=shape.shape)
        final_array = np.where(shape == 1, random_values, 0)

        return Grid.from_array(final_array)
    
    def __str__(self) -> str:
        """Return a formatted string showing the current game state:
        the live grid (with active block overlaid), score, and game over status."""
        status = "GAME OVER" if self.__is_end else "PLAYING"
        header = f"Status: {status}  |  Points: {self.__points}"
        separator = "-" * len(header)
        return f"{header}\n{separator}\n{self.get_draw_grid()}"