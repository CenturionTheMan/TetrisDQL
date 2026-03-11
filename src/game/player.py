import numpy as np
from game.player_shapes import get_all_shapes
import random




class Player:
    def __init__(self):
        self.current_shape = None
        self.change_shape()
        
    def get_width(self) -> int:
        return self.current_shape.shape[1]
    
    def get_height(self) -> int:
        return self.current_shape.shape[0]
    
    def change_shape(self) -> None:
        all_shapes = get_all_shapes()
        self.current_shape = random.choice(all_shapes)
        
    def remove_shape(self) -> None:
        self.current_shape = None
        
    def is_falling(self) -> bool:
        return self.current_shape is not None
        
    def get_shape(self) -> np.ndarray:
        return self.current_shape