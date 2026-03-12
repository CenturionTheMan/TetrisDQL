import numpy as np
from game.logic.vec2 import Vec2


class Grid:
    """A 2D integer grid backed by a NumPy array. Used to represent the Tetris board."""

    # -------------------------------------------------------------------------
    # Initialization
    # -------------------------------------------------------------------------

    def __init__(self, size: Vec2):
        """Create a grid of the given size, filled with zeros."""
        self.map = np.zeros(shape=(size.get_y(), size.get_x()), dtype=np.int32)

    # -------------------------------------------------------------------------
    # Map access
    # -------------------------------------------------------------------------

    def get_map(self) -> np.ndarray:
        """Return the raw NumPy array backing the grid."""
        return self.map

    def set_map(self, new_map: np.ndarray) -> None:
        """Replace the entire grid with the given NumPy array."""
        self.map = new_map

    def get_shape(self) -> Vec2:
        """Return the grid dimensions as a Vec2(width, height)."""
        return Vec2(self.map.shape[1], self.map.shape[0])

    def copy(self) -> "Grid":
        """Return a deep copy of this grid."""
        g = Grid(self.get_shape())
        g.set_map(self.map.copy())
        return g        

    # -------------------------------------------------------------------------
    # Bounds checking
    # -------------------------------------------------------------------------

    def is_pos_in_bounds(self, pos: Vec2) -> bool:
        """Return True if the given position lies within the grid boundaries."""
        return (
            pos.get_x() >= 0 and pos.get_x() < self.map.shape[1] and
            pos.get_y() >= 0 and pos.get_y() < self.map.shape[0]
        )

    def is_gird_overlap(self, grid: "Grid", offset: Vec2) -> bool:
        """Return True if the given grid overlaps with this grid at the specified offset.
        Checks for both out-of-bounds and non-zero cell collisions."""
        if grid is None:
            return False
        tmp_shape = grid.get_shape()
        for x in range(tmp_shape.get_x()):
            for y in range(tmp_shape.get_y()):
                v = grid.get_value(x, y)
                if v == 0:
                    continue  # Empty cell, no collision

                x_g = offset.get_x() + x
                y_g = offset.get_y() + y
                
                if not self.is_pos_in_bounds(Vec2(x_g, y_g)):
                    return True  # Out of bounds counts as a collision
                if self.get_value(x_g, y_g) != 0:
                    return True  # Non-zero cell collision
        return False


    # -------------------------------------------------------------------------
    # Reading values
    # -------------------------------------------------------------------------

    def get_value(self, x: int, y: int) -> int:
        """Return the value at position (x, y)."""
        return self.map[y][x]

    def check_if_row_has_any_zeros(self, row_idx: int) -> bool:
        """Return True if the given row contains at least one empty (zero) cell."""
        for x in range(self.map.shape[1]):
            if self.map[row_idx][x] == 0:
                return True
        return False

    # -------------------------------------------------------------------------
    # Writing values
    # -------------------------------------------------------------------------

    def set_value(self, x: int, y: int, value: int) -> None:
        """Set the cell at (x, y) to the given value. No bounds check."""
        self.map[y][x] = value

    def try_set_value(self, x: int, y: int, value: int) -> bool:
        """Set the cell at (x, y) if the position is in bounds.
        Returns True on success, False if out of bounds."""
        if self.is_pos_in_bounds(Vec2(x, y)):
            self.map[y][x] = value
            return True
        return False

    # -------------------------------------------------------------------------
    # Display
    # -------------------------------------------------------------------------

    def __str__(self) -> str:
        """Return a formatted string of the grid with column letters and row numbers.
        Each cell is padded to 3 characters wide."""
        
        from game.console_ui.console_colors import Fore, Style
        
        rows, cols = self.map.shape

        col_letters = [chr(ord('A') + i) for i in range(cols)]
        header = "     " + "  ".join(f"{l:>3}" for l in col_letters)

        lines = [header]
        for y in range(rows):
            row_cells = []
            for x in range(cols):
                v = self.map[y][x]
                if v > 0:
                    cell = f"{Fore.CYAN}{'█':>3}{Style.RESET_ALL}"
                elif v < 0:
                    cell = f"{Fore.YELLOW}{'█':>3}{Style.RESET_ALL}"
                else:
                    cell = f"{'.'  :>3}"
                row_cells.append(cell)
            row_str = f"{y:>3} |" + "  ".join(row_cells)
            lines.append(row_str)

        return "\n".join(lines)