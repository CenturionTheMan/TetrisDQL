from typing import Tuple
import numpy as np
from game.player import Player
from game.vec2 import Vec2, VEC_DOWN, VEC_LEFT, VEC_RIGHT, VEC_UP
from game.grid import Grid
import random

class TetrisHandler(object):
    def __init__(self, gird_size:Tuple[int,int] = (16,8)):
        self.grid = Grid(Vec2(gird_size[0], gird_size[1]))
        self.player = Player()
        
        player_height = self.player.get_size().get_y()
        self.player_top_left = Vec2(0,-player_height) #! y,x
        self.points = 0
        self.is_end = False
        
    def update(self) -> None:
        if self.is_end:
            return
        
        if self.player.is_falling():
            
            if self.has_player_collided():
                self.add_player_shape_to_grid()
                self.player.remove_block()
            else:
                self.player_top_left += VEC_DOWN 
                
        else:
            _ = self.check_rows_fulfillment()
            
            if self.check_end_condition():
                return
            
            self.create_player_block()
    
    def is_game_over(self) -> bool:
        return self.is_end
    
    def check_end_condition(self) -> bool:
        for x in range(self.grid.get_shape().get_x()):
            if self.grid.get_value(x,0) != 0:
                self.is_end = True
                return True
        return False
    
    def create_player_block(self) -> None:
        if self.player.get_block() is not None:
            return
        self.player.change_block()
        self.player_top_left = Vec2(
            random.randint(0, self.grid.get_shape().get_x() - self.player.get_size().get_x()), 
            -self.player.get_size().get_y())
        
    
    def add_player_shape_to_grid(self):
        block = self.player.get_block()
        shape = block.get_shape()
        pbl = self.player_top_left
        
        for x in range(shape.get_x()):
            for y in range(shape.get_y()):
                v = block.get_value(x,y)
                if v != 0:
                    self.grid.set_value(pbl.get_x() + x, pbl.get_y() + y, v)
    
    def has_player_collided(self): #Would collide on next frame
        pblc = self.player_top_left
        block = self.player.get_block()
        shape = block.get_shape()
        
        for xp in range(shape.get_x()):
            for yp in range(shape.get_y()):
                val = block.get_value(xp,yp)
                if val == 0:
                    continue
                y_tmp = yp + pblc.get_y()
                
                if y_tmp < 0:
                    continue #player pixel above
                
                x_g, y_g = pblc.get_x() + xp, y_tmp + 1
                
                if not self.grid.is_pos_in_bounds(Vec2(x_g, y_g)):
                    return True #player pixel would be out of bounds
                
                v_g = self.grid.get_value(x_g, y_g)
                
                if v_g != 0:
                    return True
        return False
    
    
    def check_rows_fulfillment(self) -> True:
        to_remove = []
        for row_idx in range(self.grid.get_shape().get_y()):
            has_zeros = self.grid.check_if_row_has_any_zeros(row_idx)
            if not has_zeros:
                to_remove.append(row_idx)
        if len(to_remove) == 0:
            return False
        
        self.points += len(to_remove)
        
        for row_idx in to_remove:
            for y in range(row_idx, 0, -1):
                for x in range(self.grid.get_shape().get_x()):
                    self.grid.set_value(x,y,self.grid.get_value(x,y-1))
        return True
    
    def get_point(self) -> int:
        return self.points
        
        
    def get_draw_grid(self) -> Grid:
        tmp_grid = self.grid.copy()
        
        if self.player.get_block() is None:
            return tmp_grid
        
        block = self.player.get_block()
        shape = block.get_shape()
        pbl = self.player_top_left
        
        for x in range(shape.get_x()):
            for y in range(shape.get_y()):
                v = block.get_value(x,y)
                if v != 0:
                    px, py = pbl.get_x() + x, pbl.get_y() + y
                    _ = tmp_grid.try_set_value(px, py, v)
        return tmp_grid