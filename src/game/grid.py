import numpy as np
from game.vec2 import Vec2


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
        rows, cols = self.map.shape

        # Header row with column letters (A, B, C, ...)
        col_letters = [chr(ord('A') + i) for i in range(cols)]
        header = "     " + "  ".join(f"{l:>3}" for l in col_letters)

        lines = [header]
        for y in range(rows):
            row_str = f"{y:>3} |" + "  ".join(f"{self.map[y][x]:>3}" for x in range(cols))
            lines.append(row_str)

        return "\n".join(lines)