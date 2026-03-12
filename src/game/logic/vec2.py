class Vec2:
    """A 2D integer vector with x and y components."""

    def __init__(self, x: int, y: int):
        """Initialize the vector with the given x and y values."""
        self.set_val(x, y)

    def get_x(self) -> int:
        """Return the x component."""
        return self.__x

    def get_y(self) -> int:
        """Return the y component."""
        return self.__y

    def __add__(self, other: "Vec2") -> "Vec2":
        """Return a new Vec2 that is the sum of this vector and another."""
        return Vec2(self.__x + other.get_x(), self.__y + other.get_y())

    def __repr__(self) -> str:
        """Return a string representation of the vector."""
        return f"Vec2({self.__x}, {self.__y})"

    def set_val(self, x, y) -> None:
        """Set both x and y components at once."""
        self.__x = x
        self.__y = y


# Cardinal direction unit vectors for convenience
VEC_DOWN  = Vec2(0,  1)  # Positive Y axis (down)
VEC_UP    = Vec2(0, -1)  # Negative Y axis (up)
VEC_RIGHT = Vec2(1,  0)  # Positive X axis (right)
VEC_LEFT  = Vec2(-1, 0)  # Negative X axis (left)