from typing import List
import numpy as np

SHAPE_O = np.array([
    [1 ,1],
    [1, 1]
])

SHAPE_I = np.array([
    [1],
    [1],
    [1],
    [1]
])

SHAPE_S = np.array([
    [0 ,1, 1],
    [1, 1, 0]
])

SHAPE_Z = np.array([
    [1 ,1, 0],
    [0, 1, 1]
])

SHAPE_L = np.array([
    [1 ,0],
    [1 ,0],
    [1, 1]
])

SHAPE_J = np.array([
    [0 ,1],
    [0 ,1],
    [1, 1]
])


SHAPE_T = np.array([
    [1 ,1, 1],
    [0, 1, 0]
])

def get_all_shapes() -> List[np.ndarray]:
    return [SHAPE_O, SHAPE_I, SHAPE_S, SHAPE_Z, SHAPE_L, SHAPE_J, SHAPE_T]
    