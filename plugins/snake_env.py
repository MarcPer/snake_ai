import gym
import numpy as np
from gym import spaces

APPLE_REWARD = 1
DEATH_PENALTY = -1
SNAKE_GROWTH = 2

class SnakeEnv(gym.Env):
    APPLE_GRID_VAL = 3
    HEAD_GRID_VAL = 2
    COLL_GRID_VAL = 1

    def __init__(self, grid_size=40, seed=None):
        if seed:
            np.random.seed(seed)
        self.curr_dir = None
        self.grid_size = grid_size
        self.extend = 0
        self.snake_length = 0
        self._reset_state()
        self.action_space = spaces.Discrete(3) # 0 do nothing, 1 turn left, 2 turn right
        self.observation_space = spaces.Box(0, 3, (self.grid_size, self.grid_size, 1))
        self.reward_range = (-5, APPLE_REWARD + 1)
        self.arena_length = self.grid_size * self.grid_size

    def _reset_state(self):
        self.curr_dir = 'l'
        self.extend = 0
        self.snake = self.build_snake()
        self.apple = self.spawn_apple()

    def build_snake(self):
        """Returns a list of contiguous coordinates forming the snake, and
        starting from the head. The snake size and position depends on the
        size of the arena."""
        self.snake_length = max([self.grid_size // 6, 2])
        head_posy = self.grid_size // 2 + 1
        head_posx = self.grid_size // 2 + 1
        return list(map(lambda y: (head_posy + y, head_posx), range(self.snake_length)))

    def reset(self):
        self._reset_state()
        return self.normalize_state()

    def spawn_apple(self, observation=None):
        """Spawn apple in a random position, retrying if it happens
        to fall on the snake. When snake gets long enough, adopt a different
        strategy, finding empty spaces first and randomly selecting among
        them."""

        # If snake is already too big, don't use brute force method
        if observation is not None and (self.snake_length >= 2*self.arena_length//3):
            pos_array = np.arange(self.arena_length).reshape(self.grid_size, self.grid_size)
            empty_pos = np.multiply(pos_array, observation.squeeze() == 0)
            empty_pos = empty_pos[empty_pos != 0]
            if empty_pos.size == 0:
                return None
            pos_idx = np.random.choice(empty_pos)
            return (pos_idx // self.grid_size, pos_idx % self.grid_size)

        apple_pos = tuple(np.random.randint(self.grid_size, size=2))
        if self.collides(apple_pos, self.snake):
            return self.spawn_apple()
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

        if (snake_head[0] < 0) or (snake_head[0] >= self.grid_size) or (snake_head[1] < 0) or (snake_head[1] >= self.grid_size):
            done = True
        elif self.collides(snake_head, self.snake[1:-1]):
            done = True

        observation = self.normalize_state()
        if done:
            reward -= abs(DEATH_PENALTY)
        elif self.collides(self.apple, self.snake[0:1]):
            reward += APPLE_REWARD
            self.extend += SNAKE_GROWTH
            self.apple = self.spawn_apple(observation)
            if self.apple:
                observation[self.apple[0], self.apple[1], 0] = self.APPLE_GRID_VAL

        if self.snake_length > self.arena_length:
            return observation, reward, True, {}

        return observation, reward, done, {}

    def move(self):
        snake_head = self.snake[0]
        if self.extend >= 0:
            new_tail = self.snake
            self.extend -= 1
            self.snake_length += 1
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
        out = np.zeros((self.grid_size, self.grid_size), dtype=np.uint8)
        if self.apple:
            out[self.apple[0], self.apple[1]] = self.APPLE_GRID_VAL

        head_y, head_x = self.snake[0]
        if head_x >= 0 and head_x < self.grid_size and head_y >= 0 and head_y < self.grid_size:
            out[head_y, head_x] = self.HEAD_GRID_VAL

        for (y, x) in self.snake[1:-1]:
            if x < 0 or x >= self.grid_size or y < 0 or y >= self.grid_size:
                continue
            out[y, x] = self.COLL_GRID_VAL
        return np.reshape(out, (self.grid_size, self.grid_size, 1))

    def render(self, mode='human'):
        norm_state = np.array(np.squeeze(self.normalize_state()))
        full_grid = np.zeros((self.grid_size + 2, self.grid_size + 2))

        # Add val elements
        full_grid[0,:] = self.COLL_GRID_VAL
        full_grid[self.grid_size+1,:] = self.COLL_GRID_VAL
        full_grid[:,0] = self.COLL_GRID_VAL
        full_grid[:,self.grid_size+1] = self.COLL_GRID_VAL

        full_grid[1:(self.grid_size+1), 1:(self.grid_size+1)] = norm_state

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
