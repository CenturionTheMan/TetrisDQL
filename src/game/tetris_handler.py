from typing import Tuple
import numpy as np
from game.player import Player
from game.vec2 import Vec2, VEC_DOWN, VEC_LEFT, VEC_RIGHT, VEC_UP
from game.grid import Grid

class TetrisHandler(object):
    def __init__(self, gird_size:Tuple[int,int] = (16,8)):
        self.grid = Grid(Vec2(gird_size[0], gird_size[1]))
        self.player = Player()
        self.player_bottom_left = Vec2(0,0) #! y,x
        self.points = 0
        self.is_end = False
        
    def update(self) -> None:
        if self.player.is_falling(): #if player is still falling then we need to check if it has collided with something
            if self.has_player_collided():
                self.add_player_shape_to_grid()
                self.player.remove_shape()
            else:
                #TODO check left/right input request -> move player one block if so
                self.player_bottom_left.add(VEC_DOWN) # move player one block down
        else:
            # if self.check_rows_fulfillment(): #check rows to remove if row full 
            #     return #if rows were deleted wait for one iteration
            #TODO check if ony column full -> end game
            #TODO setup player new position and shape
            pass
    
    def add_player_shape_to_grid(self):
        block = self.player.get_block()
        shape = block.get_shape()
        pbl = self.player_bottom_left
        
        for x in range(shape.get_x()):
            for y in range(shape.get_y()):
                v = block.get_value(x,y)
                if v != 0:
                    self.grid.set_value(pbl.get_x() + x, pbl.get_y() + y, v)
    
    def has_player_collided(self): #Would collide on next frame
        pblc = self.player_bottom_left
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
    
    
    def check_rows_fulfillment(self) -> bool:
        for y in range(self.grid.get_size().get_y()):
            if self.is_row_full(y):
                self.delete_row(y)
                return True
        return False
    
    def is_row_full(self, y) -> bool:
        for x in range(self.grid.get_size().get_x()):
            if self.grid.get_value(x,y) == 0:
                return False
        return True
    
    def delete_row(self, y) -> None:
        for x in range(self.grid.get_size().get_x()):
            self.grid.set_value(x,y,0)
        
        for y_tmp in range(y-1, -1, -1):
            for x in range(self.grid.get_size().get_x()):
                val = self.grid.get_value(x,y_tmp)
                self.grid.set_value(x,y_tmp+1,val)
        
        
    def get_draw_grid(self) -> Grid:
        tmp_grid = self.grid.copy()
        
        if self.player.get_block() is None:
            return tmp_grid
        
        block = self.player.get_block()
        shape = block.get_shape()
        pbl = self.player_bottom_left
        
        for x in range(shape.get_x()):
            for y in range(shape.get_y()):
                v = block.get_value(x,y)
                if v != 0:
                    tmp_grid.set_value(pbl.get_x() + x, pbl.get_y() + y, v)
        return tmp_grid