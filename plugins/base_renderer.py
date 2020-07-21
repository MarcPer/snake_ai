"""Basic renderer interface.
"""

class BaseRenderer:
    def __init__(self, env):
        pass

    def types(self):
        return ["renderer"]

    def render(self, _state, _score):
        pass

    def set_caption(self, _caption):
        pass
