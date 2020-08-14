import pickle
from os import path
import numpy as np


def load_memory(filename):
    fullname = path.join('recordings', filename)
    mem = []
    with open(fullname, 'rb') as f:
        while True:
            try:
               mem.append(pickle.load(f))
            except EOFError:
                break
    return mem

class MemoryPlayback():
    GRID_SIZE = 40
    APPLE_GRID_VAL = 3
    HEAD_GRID_VAL = 2
    COLL_GRID_VAL = 1

    def __init__(self, filename):
        self.memory = load_memory(filename)
        self.memory_len = len(self.memory)
        if self.memory_len == 0:
            raise SystemError("Nothing recorded in memory file {filename}")
        self.curr_dir = self.memory[0][3]
        self.grid_size = np.array(self.memory[0][0]).shape[0]
        self.offset = 0

    def reset(self):
        self.offset = 0
        self.curr_dir = self.memory[0][3]
        return self.memory[0][0]

    def step(self, _action):
        if self.offset >= self.memory_len - 1:
            state = self.memory[self.offset][0]
            return state, 0, True, None
        self.offset += 1
        state, reward, done, curr_dir, _rec_action = self.memory[self.offset]
        self.curr_dir = curr_dir
        return state, reward, done, None

    def render(self, mode='human'):
        norm_state = np.array(np.squeeze(self.memory[self.offset][0]))
        full_grid = np.zeros((self.GRID_SIZE + 2, self.GRID_SIZE + 2))

        # Add val elements
        full_grid[0,:] = self.COLL_GRID_VAL
        full_grid[self.GRID_SIZE+1,:] = self.COLL_GRID_VAL
        full_grid[:,0] = self.COLL_GRID_VAL
        full_grid[:,self.GRID_SIZE+1] = self.COLL_GRID_VAL

        full_grid[1:(self.GRID_SIZE+1), 1:(self.GRID_SIZE+1)] = norm_state

        size_y, size_x = full_grid.shape
        for y in range(size_y):
            for x in range(size_x):
                cell_val = full_grid[y, x]
                if cell_val == self.APPLE_GRID_VAL:
                    print('o', end='')
                elif cell_val == self.HEAD_GRID_VAL:
                    print('H', end='')
                elif cell_val == self.COLL_GRID_VAL:
                    print('#', end='')
                else:
                    print(' ', end='')
            print('')
