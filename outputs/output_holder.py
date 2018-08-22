"""
This is the OutputHolder class.

This class helps streamers reuse camera ports for the same format and size combination
by passing the captured content through the various output analysers
"""

from time import sleep
from collections import deque
from threading import Thread, Event, Lock
from concurrent.futures import ThreadPoolExecutor

class OutputHolder:
    def __init__(self, outputs = {}):
        self.outputs = outputs
        self.outputs_to_add = {}
        self.writable = False
        self.output_lock = Lock()
        self.pool = ThreadPoolExecutor()  # Don't specify max_workers, let system decide according to CPUs
        self.writer_thread = None

    def has_outputs(self):
        return len(self.outputs) > 0

    def has_output(self, output_id):
        return output_id in self.outputs.keys()

    def get_output(self, output_id):
        return self.outputs[output_id]

    def add_output(self, output_id, output):
        with self.output_lock:
            self.outputs[output_id] = output

    def prepare_new_output(self, output_id, output):
        self.outputs_to_add[output_id] = output

    def remove_output(self, output_id):
        with self.output_lock:
            del self.outputs[output_id]

class WriterOutputHolder(Thread, OutputHolder):
    def __init__(self, outputs = {}):
        Thread.__init__(self)
        OutputHolder.__init__(self, outputs)
        self.aux_buffer = deque()
        self.rebind_wait = Event()

    def write(self, buffer):
        """
        write method must return fast in order not to slow down the framerate
        """
        self.aux_buffer.append(buffer)

    def wait_for_rebind(self):
        self.rebind_wait.wait()
        self.rebind_wait.clear()

    def notify_split(self):
        self.aux_buffer.append(True)

    def run(self):
        self.writable = True
        while self.writable:
            try:
                buffer = self.aux_buffer.popleft()
                #  Check if its a split notifier
                if type(buffer) is bool:
                    for out_id, out in self.outputs_to_add.items():
                        print("Changing output with id: %s" % out_id)
                        self.outputs[out_id] = out
                    self.outputs_to_add = {}
                    self.rebind_wait.set()
                    continue

                futures = []
                with self.output_lock:
                    for _, output in self.outputs.items():
                        futures.append(self.pool.submit(output.write, buffer))  # Using pool because instantiating Threads on every write is pretty slow    
                    for future in futures:
                        future.result()  # Simply wait for the writing to finish.
            except IndexError:
                sleep(0.05)
                continue

    def stop(self):
        self.writable = False