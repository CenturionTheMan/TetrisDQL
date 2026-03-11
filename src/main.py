from game.tetris_handler import TetrisHandler


game = TetrisHandler()

for i in range(100):
    grid = game.get_gird()
    shape = grid.shape
    
    for x in range(shape[0]):
        for y in range(shape[1]):
            print(grid[x][y], end=" ")
        print()
        
    game.update()
    print()