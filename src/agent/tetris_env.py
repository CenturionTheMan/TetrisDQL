import numpy as np
from game.logic.tetris_handler import TetrisHandler


class TetrisEnv:
    """Gym-like environment wrapper for TetrisHandler.

    Actions:
        0 = move left
        1 = move right
        2 = rotate clockwise
        3 = rotate counter-clockwise
        4 = no-op (just let gravity tick)

    State:
        Flattened draw grid (10*20 = 200 values), normalized to [0, 1].

    Reward:
        +points_delta  when rows are cleared (sum² scoring)
        -10            on game over
        +0.01          per survived tick (encourages staying alive)
    """

    NUM_ACTIONS = 5
    GRID_WIDTH = 10
    GRID_HEIGHT = 20

    def __init__(self):
        self.game: TetrisHandler | None = None
        self.state_size = self.GRID_WIDTH * self.GRID_HEIGHT
        self.reset()

    def reset(self) -> np.ndarray:
        """Reset the game and return the initial state."""
        self.game = TetrisHandler((self.GRID_WIDTH, self.GRID_HEIGHT))
        return self._get_state()

    def step(self, action: int) -> tuple[np.ndarray, float, bool]:
        """Execute one action + one gravity tick.

        Returns:
            state:  new observation (flattened grid)
            reward: reward for this step
            done:   True if game over
        """
        points_before = self.game.get_points()

        # Apply action
        if action == 0:
            self.game.try_move(is_right=False)
        elif action == 1:
            self.game.try_move(is_right=True)
        elif action == 2:
            self.game.try_rotate(is_clockwise=True)
        elif action == 3:
            self.game.try_rotate(is_clockwise=False)
        # action == 4: no-op

        # Gravity tick
        self.game.update()

        done = self.game.is_game_over()
        points_after = self.game.get_points()
        points_delta = points_after - points_before

        # Reward
        reward = float(points_delta)
        if done:
            reward -= 10.0
        else:
            reward += 0.01  # survival bonus

        return self._get_state(), reward, done

    def _get_state(self) -> np.ndarray:
        """Return the current grid (with active block) as a flat float32 array, normalized."""
        grid = self.game.get_draw_grid().get_map().flatten().astype(np.float32)
        # Normalize: values range roughly from -10 to 10, map to [0, 1]
        grid = (grid + 10.0) / 20.0
        return grid
