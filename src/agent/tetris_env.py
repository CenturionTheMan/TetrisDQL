from typing import Literal

import numpy as np
from game.logic.tetris_handler import TetrisHandler


class TetrisEnv:

    GRID_WIDTH = 10
    GRID_HEIGHT = 20
    # STATE_SIZE = GRID_WIDTH + 4 + GRID_HEIGHT * 2  # heights, holes, bumpiness, max_height, lines_cleared + (fill_ratio, avg_value) per row
    STATE_SIZE = GRID_WIDTH * 4 + 4 + GRID_HEIGHT * 2
    
    def __init__(self, score_algorithm: Literal['SQUARE_OF_SUM', 'CONSTANT'] = "SQUARE_OF_SUM"):
        self.score_algorithm = score_algorithm
        self.game: TetrisHandler | None = None
        self.state_size = self.STATE_SIZE
        self.reset()

    def reset(self) -> list:
        self.game = TetrisHandler(score_algorithm=self.score_algorithm, gird_size=(self.GRID_WIDTH, self.GRID_HEIGHT))
        return self.get_valid_placements()

    def step(self, action_idx: int) -> tuple[list, float, bool]:

        placements = self.get_valid_placements() # dostajemy możliwe położenia klocka na całej mapie
        if not placements: # jeśli nie ma miejsca to koniec gry
            return [], -5.0, True

        action_idx = min(action_idx, len(placements) - 1) # zabezpieczenie jeśli sieć zwróci za duży indeks
        rotations, col, _, sim_reward = placements[action_idx] # ilość rotacji, ustaw na col

        self.game.execute_placement(rotations, col) # ustawiamy klocek
        done = self.game.is_game_over() # sprawdzamy czy koniec gry

        reward = sim_reward # nagroda = suma kwadratów wartości klocków ze zbitych wierszy
        if done:
            reward -= 10.0 if self.score_algorithm == "SQUARE_OF_SUM" else 5.0

        if done:
            return [], reward, True

        return self.get_valid_placements(), reward, False

    def get_valid_placements(self) -> list:

        block = self.game.get_player_block() # jaki klocek jest obecnie
        if block is None:  # jeśli nie ma
            return []

        grid_map = self.game.get_grid().get_map()   # dostajemy mapę
        block_map = block.get_map() # dostajemy figurę jako tablice

        placements = []
        seen = set()  # unikamy zduplikowanych stanów planszy (symetryczne rotacje)

        for rotations in range(4):
            rotated = np.rot90(block_map, k=-rotations)   # rotations krotne obroty zgodnie z ruchem wskazówek
            rh, rw = rotated.shape

            for col in range(self.GRID_WIDTH):
                in_bounds = all(
                    0 <= col + bc < self.GRID_WIDTH
                    for br in range(rh)
                    for bc in range(rw)
                    if rotated[br, bc] != 0
                ) # sprawdzamy czy klocek się mieści w mapie
                if not in_bounds:
                    continue

                result = self._simulate_drop(grid_map, rotated, col) # zrzucamy klocek na dół
                if result is None:
                    continue
 
                result, lines_cleared, sim_reward = self._clear_lines(result) # czyścimy linie jeśli pełna

                key = result.tobytes() # unikalny id planszy
                if key in seen:
                    continue
                seen.add(key)

                features = self._compute_features(result, lines_cleared)
                placements.append((rotations, col, features, sim_reward)) # dodajemy stan

        return placements

    def _simulate_drop(self, grid_map: np.ndarray, block_map: np.ndarray, col: int) -> np.ndarray | None:
        rows = grid_map.shape[0]
        bh, bw = block_map.shape

        # Opuść klocek tak nisko, jak to możliwe
        drop_row = -bh
        while self._can_place(grid_map, block_map, col, drop_row + 1):
            drop_row += 1

        # Klocek musi mieć przynajmniej jedną komórkę wewnątrz siatki
        any_in_grid = any(
            0 <= drop_row + br < rows and block_map[br, bc] != 0
            for br in range(bh)
            for bc in range(bw)
        )
        if not any_in_grid:
            return None

        result = grid_map.copy()
        for br in range(bh):
            for bc in range(bw):
                if block_map[br, bc] != 0:
                    gr = drop_row + br
                    gc = col + bc
                    if 0 <= gr < rows:
                        result[gr, gc] = block_map[br, bc]
        return result

    def _can_place(self, grid_map: np.ndarray, block_map: np.ndarray, col: int, row: int) -> bool:
        """Sprawdź czy klocek może być umieszczony w pozycji (col, row) bez kolizji."""
        rows, cols = grid_map.shape
        for br in range(block_map.shape[0]):
            for bc in range(block_map.shape[1]):
                if block_map[br, bc] == 0:
                    continue
                gr = row + br
                gc = col + bc
                if gc < 0 or gc >= cols:
                    return False
                if gr >= rows:
                    return False
                if gr >= 0 and grid_map[gr, gc] != 0:
                    return False
        return True

    def _clear_lines(self, grid_map: np.ndarray) -> tuple[np.ndarray, int, float]:
        """Usuń pełne wiersze i zwróć (nowa_siatka, liczba_wyczyszczonych, nagroda)."""
        full = np.all(grid_map != 0, axis=1)
        n = int(full.sum())
        if n == 0:
            return grid_map, 0, 0.0
        if self.score_algorithm == "CONSTANT":
            cleared_reward = float(n)
        elif self.score_algorithm == "SQUARE_OF_SUM":
            cleared_reward = float(sum(np.sum(row) ** 2 for row in grid_map[full])) * 1.5
        else:
            raise ValueError(f"Unknown score algorithm: {self.score_algorithm}")
        kept = grid_map[~full]
        empty = np.zeros((n, grid_map.shape[1]), dtype=grid_map.dtype)
        new_grid = np.vstack([empty, kept])
        return new_grid, n, cleared_reward

    def _compute_features(self, grid_map: np.ndarray, lines_cleared: int) -> np.ndarray:
        heights = np.zeros(self.GRID_WIDTH, dtype=np.float32)
        for col in range(self.GRID_WIDTH):
            for row in range(self.GRID_HEIGHT):
                if grid_map[row, col] != 0:
                    heights[col] = self.GRID_HEIGHT - row
                    break

        holes = 0
        for col in range(self.GRID_WIDTH):
            found_block = False

            for row in range(self.GRID_HEIGHT):

                if grid_map[row, col] != 0:
                    found_block = True

                elif found_block:
                    holes += 1

        bumpiness = float(np.sum(np.abs(np.diff(heights))))
        max_height = float(np.max(heights))
        col_value_sum = np.zeros(self.GRID_WIDTH, dtype=np.float32)
        col_max = np.zeros(self.GRID_WIDTH, dtype=np.float32)
        high_value_count = np.zeros(self.GRID_WIDTH, dtype=np.float32)

        for col in range(self.GRID_WIDTH):
            column_cells = np.abs(grid_map[:, col])
            col_value_sum[col] = np.sum(column_cells)
            col_max[col] = np.max(column_cells)
            high_value_count[col] = np.sum(column_cells >= 7)

        col_value_sum_norm = col_value_sum / (self.GRID_HEIGHT * 9.0)
        col_max_norm = col_max / 9.0
        high_value_count_norm = high_value_count / self.GRID_HEIGHT

        row_features = []

        for row in range(self.GRID_HEIGHT):
            cells = np.abs(grid_map[row])
            fill = np.count_nonzero(cells) / self.GRID_WIDTH
            avg_val = np.mean(cells) / 9.0
            row_features.extend([fill, avg_val])

        return np.array([
                *heights / self.GRID_HEIGHT,
                *col_value_sum_norm,
                *col_max_norm,
                *high_value_count_norm,
                holes / (self.GRID_WIDTH * self.GRID_HEIGHT),
                bumpiness / (self.GRID_WIDTH * self.GRID_HEIGHT),
                max_height / self.GRID_HEIGHT,
                lines_cleared / 4.0,
                *row_features], dtype=np.float32)
