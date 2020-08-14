"""Records gameplay on a local file.
"""

import pickle
from os import path
from queue import Empty, Queue
import threading
import time


from plugins.base_aux import BaseAux

class MemoryRecorder(BaseAux):
    """Records gameplay into a file, which can
    be played back with MemoryPlayback plugin."""
    def __init__(self, filename):
        BaseAux.__init__(self)
        self.memory = []
        fullname = path.join('recordings', filename)
        self.filename = fullname
        with open(fullname, 'wb') as _f:
            pass
        self.queue = Queue()
        self.quit = threading.Event() # Signals to thread when to stop
        self.file_thread = threading.Thread(
            name='file_flush',
            target=_bg_run,
            args=(self.quit, self.queue, self.filename))
        self.file_thread.start()

    def run(self, state, reward, done, curr_dir, action):
        """Appends state to queue to be consumed by background thread.
        """
        self.queue.put([state, reward, done, curr_dir, action])

    def close(self):
        """Signal bg thread to stop, pushing remaining states to file.
        """
        self.quit.set()
        self.file_thread.join()

def _bg_run(quit_ev, memory, filename):
    """Background thread polls queue for states to save,
    and appends to a file. The poll is non-blocking, so
    that the thread can get the signal to stop.
    Once the signal arrives, it pushes all remaining states
    from memory to the given file.
    """
    done = False
    while not done:
        try:
            with open(filename, 'ab') as f:
                while not memory.empty():
                    item = memory.get(block=False)
                    pickle.dump(item, f)
        except Empty:
            pass
        done = quit_ev.is_set()
        if not done:
            time.sleep(1)
