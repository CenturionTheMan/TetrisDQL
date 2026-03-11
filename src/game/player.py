import numpy as np
from game.player_blocks import get_all_blocks
import random
from game.vec2 import Vec2
from game.grid import Grid


class Player:
    def __init__(self):
        self.current_block : Grid = None
        self.change_block()
        
    def get_size(self) -> Vec2:
        return self.current_block.get_shape()
    
    def change_block(self) -> None:
        all_blocks = get_all_blocks()
        rnd = random.choice(all_blocks)
        grid = Grid(Vec2(0,0))
        grid.set_map(rnd)
        self.current_block = grid
        
    def remove_block(self) -> None:
        self.current_block = None
        
    def is_falling(self) -> bool:
        return self.current_block is not None
    
    def get_block(self) -> Grid:
        return self.current_block