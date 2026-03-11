from typing import Tuple
import numpy as np
from game.player import Player

class TetrisHandler(object):
    def __init__(self, gird_size:Tuple[int,int] = (16,8)):
        self.grid = np.zeros(shape=gird_size, dtype=np.int32)
        self.player = Player()
        self.player_bottom_left_corner = (0,0)
        self.points = 0
        self.is_end = False
        
    def update(self) -> None:
        if self.player.is_falling(): #if player is still falling then we need to check if it has collided with something
            if self.has_player_collided():
                self.add_player_shape_to_grid()
                self.player.remove_shape()
            else:
                #TODO check left/right input request -> move player one block if so
                #TODO move player one block down
                pass
        else:
            if self.check_rows_fulfillment(): #check rows to remove if row full 
                return #if rows were deleted wait for one iteration
            #TODO check if ony column full -> end game
            #TODO setup player new position and shape
            pass
    
    def add_player_shape_to_grid(self):
        player_shape = self.player.get_shape()
        pblc = self.player_bottom_left_corner
        
        for x in range(player_shape.shape[0]):
            for y in range(player_shape.shape[1]):
                if player_shape[x][y] != 0:
                    self.grid[pblc[0] + x][pblc[1] + y] = player_shape[x][y]
    
    def has_player_collided(self):
        player_shape = self.player.get_shape()
        
        pblc = self.player_bottom_left_corner
        
        if self.player.get_height() + pblc[1] >= self.grid.shape[0]: #if player shape is at the bottom of grid then it has collided
            return True
        
        for idx, s in enumerate(player_shape[-1]): #iterating over last row of player shape
            pixel_x = pblc[0] + idx
            pixel_y = pblc[1]
            if s == 0:
                pixel_y =- 1 #if given pos i player last row shape is zero then value one is one above
            
            if pixel_y < 0:
                continue #if player shape is above grid then we can ignore it
            if self.grid[pixel_x][pixel_y + 1] != 0:
                return True
            
        
    
    def check_rows_fulfillment(self) -> bool:
        to_remove = []
        for idx, row in enumerate(self.grid):
            if all(row != 0):
                to_remove.append(idx)
                
        if to_remove:
            self.points += len(to_remove)
            self.grid = np.delete(self.grid, to_remove, axis=0)
            new_rows = np.zeros(shape=(len(to_remove), self.grid.shape[1]), dtype=np.int32)
            self.grid = np.vstack((new_rows, self.grid))
            return True
        return False
        
        
    def get_gird(self) -> np.ndarray:
        return self.grid