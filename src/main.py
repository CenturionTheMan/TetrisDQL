from game.tetris_handler import TetrisHandler
from game.grid import Grid

game = TetrisHandler(gird_size=(5,5))
print()
for i in range(100):
    print(f"ITER={i}")
    grid = game.get_draw_grid()
    shape = grid.get_shape()
    
    for y in range(shape.get_y()):
        for x in range(shape.get_x()):
            print(f'{grid.get_value(x,y):2d}', end="")
        print()
        
    game.update()
    print()