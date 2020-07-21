"""Records gameplay on a local file.
"""

import pickle
from os import path

from plugins.base_aux import BaseAux

class MemoryRecorder(BaseAux):
    def __init__(self, filename):
        self.memory = []
        fullname = path.join('recordings', filename)
        self.filename = fullname

    def run(self, state, reward, done, curr_dir, action):
        """Appends state to memory list.
        """
        self.memory.append([state, reward, done, curr_dir, action])

    def close(self):
        """Saves memory to file.
        """
        with open(self.filename, 'wb') as f:
            pickle.dump(self.memory, f, protocol=4)

