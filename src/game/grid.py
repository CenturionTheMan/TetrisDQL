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
        self.map[pos.get_y()][pos.get_x()] = value

    def set_value(self, x:int, y:int, value: int) -> None:
        self.map[y][x] = value

    def get_value(self, pos:Vec2) -> int:
        return self.map[pos.get_y()][pos.get_x()]
    
    def get_value(self, x:int,y:int) -> int:
        return self.map[y][x]
    
    def get_shape(self) -> Vec2:
        return Vec2(self.map.shape[1], self.map.shape[0])
    
    def copy(self) -> Grid:
        g = Grid(self.get_shape())
        g.set_map(self.map.copy())
        return g