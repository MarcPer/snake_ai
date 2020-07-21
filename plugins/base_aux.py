"""Basic interface for auxiliary plugins
"""

class BaseAux:
    def __init__(self, *_args):
        pass

    def types(self):
        return ['aux']

    def run(self, state, reward, done, curr_dir, action):
        pass

