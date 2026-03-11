from game.tetris_handler import TetrisHandler
from game.grid import Grid

game = TetrisHandler(gird_size=(8,16))
print()
for i in range(200):
    if not game.is_game_over():
        print(f"ITER={i}")
        grid = game.get_draw_grid()
        
        print(grid)
            
        game.update()
        print()
    else:
        print("GAME OVER")
        break