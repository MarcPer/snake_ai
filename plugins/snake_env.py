import gym
import numpy as np
from gym import spaces

APPLE_REWARD = 1
DEATH_PENALTY = -1
SNAKE_GROWTH = 2

class SnakeEnv(gym.Env):
    GRID_SIZE = 40
    APPLE_GRID_VAL = 3
    HEAD_GRID_VAL = 2
    COLL_GRID_VAL = 1

    def __init__(self, seed = None):
        if seed:
            np.random.seed(seed)
        self.curr_dir = None
        self.extend = 0
        self._reset_state()
        self.action_space = spaces.Discrete(3) # 0 do nothing, 1 turn left, 2 turn right
        self.observation_space = spaces.Box(0, 3, (self.GRID_SIZE, self.GRID_SIZE, 1))
        self.reward_range = (-5, APPLE_REWARD + 1)

    def _reset_state(self):
        self.curr_dir = 'l'
        self.extend = 0
        self.snake = list(map(lambda x: (21+x, 19), range(6)))
        self.apple = self.spawnApple()

    def reset(self):
        self._reset_state()
        return self.normalize_state()

    def spawnApple(self):
        apple_pos = tuple(np.random.randint(self.GRID_SIZE, size=2))
        if self.collides(apple_pos, self.snake):
            return self.spawnApple()
        else:
            return apple_pos

    def collides(self, pos, list_pos):
        return pos in list_pos

    def step(self, action):
        done = False
        reward = 0
        if action == 1:
            if self.curr_dir == 'u': self.curr_dir = 'l'
            elif self.curr_dir == 'l': self.curr_dir = 'd'
            elif self.curr_dir == 'd': self.curr_dir = 'r'
            elif self.curr_dir == 'r': self.curr_dir = 'u'
        elif action == 2:
            if self.curr_dir == 'u': self.curr_dir = 'r'
            elif self.curr_dir == 'l': self.curr_dir = 'u'
            elif self.curr_dir == 'd': self.curr_dir = 'l'
            elif self.curr_dir == 'r': self.curr_dir = 'd'

        self.move()
        snake_head = self.snake[0]

        if (snake_head[0] < 0) or (snake_head[0] >= self.GRID_SIZE) or (snake_head[1] < 0) or (snake_head[1] >= self.GRID_SIZE):
            done = True
        elif self.collides(snake_head, self.snake[1:-1]):
            done = True

        if done:
            reward -= abs(DEATH_PENALTY)
        elif self.collides(self.apple, self.snake[0:1]):
            reward += APPLE_REWARD
            self.extend += SNAKE_GROWTH
            self.apple = self.spawnApple()   

        observation = self.normalize_state()
        return observation, reward, done, {}

    def move(self):
        snake_head = self.snake[0]
        if self.extend >= 0:
            new_tail = self.snake
            self.extend -= 1
        else:
            new_tail = self.snake[0:-1]
        if self.curr_dir == 'r':
            self.snake = [(snake_head[0], snake_head[1] + 1)] + new_tail
        elif self.curr_dir == 'l':
            self.snake = [(snake_head[0], snake_head[1] - 1)] + new_tail
        elif self.curr_dir == 'u':
            self.snake = [(snake_head[0] - 1, snake_head[1])] + new_tail
        elif self.curr_dir == 'd':
            self.snake = [(snake_head[0] + 1, snake_head[1])] + new_tail


    def normalize_state(self):
        out = np.zeros((self.GRID_SIZE, self.GRID_SIZE), dtype=np.uint8)
        out[self.apple[0], self.apple[1]] = self.APPLE_GRID_VAL

        head_y, head_x = self.snake[0]
        if head_x >= 0 and head_x < self.GRID_SIZE and head_y >= 0 and head_y < self.GRID_SIZE:
            out[head_y, head_x] = self.HEAD_GRID_VAL

        for (y, x) in self.snake[1:-1]:
            out[y, x] = self.COLL_GRID_VAL
        return np.reshape(out, (self.GRID_SIZE, self.GRID_SIZE, 1))

    def render(self, mode='human'):
        norm_state = np.array(np.squeeze(self.normalize_state()))
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
