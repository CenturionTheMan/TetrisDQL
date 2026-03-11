import numpy as np
from game.vec2 import Vec2

class Grid:
    def __init__(self, size: Vec2):
        self.map = np.zeros(shape=(size.get_y(), size.get_x()), dtype=np.int32)
    
    def get_map(self) -> np.ndarray:
        return self.map
    
    def set_map(self, new_map: np.ndarray) -> None:
        self.map = new_map
    
    def is_pos_in_bounds(self, pos:Vec2) -> bool:
        return pos.get_x() >= 0 and pos.get_x() < self.map.shape[1] and pos.get_y() >= 0 and pos.get_y() < self.map.shape[0]
    
    def set_value(self, pos: Vec2, value: int) -> None:
        if self.is_pos_in_bounds:
            self.map[pos.get_y()][pos.get_x()] = value
        else:
            raise IndexError(f"Position {pos} is out of bounds for grid of size {self.get_shape()}")
        
    def try_set_value(self, pos: Vec2, value: int) -> bool:
        return self.set_value(pos, value) if self.is_pos_in_bounds(pos) else False
        
    def try_set_value(self, x:int, y:int, value: int) -> bool:
        if self.is_pos_in_bounds(Vec2(x,y)):
            self.map[y][x] = value
            return True
        else:
            return False

    def check_if_row_has_any_zeros(self, row_idx):
        for x in range(self.map.shape[1]):
            if self.map[row_idx][x] == 0:
                return True
        return False
    
    def set_value(self, x:int, y:int, value: int) -> None:
        self.map[y][x] = value

    def get_value(self, pos:Vec2) -> int:
        return self.map[pos.get_y()][pos.get_x()]
    
    def get_value(self, x:int,y:int) -> int:
        return self.map[y][x]
    
    def get_shape(self) -> Vec2:
        return Vec2(self.map.shape[1], self.map.shape[0])
    
    def copy(self) -> "Grid":
        g = Grid(self.get_shape())
        g.set_map(self.map.copy())
        return g
    
    
    def __str__(self) -> str:
        rows, cols = self.map.shape
        
        col_letters = [chr(ord('A') + i) for i in range(cols)]
        header = "     " + "  ".join(f"{l:>3}" for l in col_letters)
        
        lines = [header]
        for y in range(rows):
            row_str = f"{y:>3} |" + "  ".join(f"{self.map[y][x]:>3}" for x in range(cols))
            lines.append(row_str)
        
        return "\n".join(lines)