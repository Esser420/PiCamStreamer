"""
This is the OutputHolder class.

This class helps streamers reuse camera ports for the same format and size combination
by passing the captured content through the various output analysers
"""

from threading import Thread

class OutputHolder:
    def __init__(self, outputs = {}, motion_outputs = {}):
        self.outputs = outputs
        self.motion_outputs = motion_outputs

    def has_outputs(self):
        return len(self.outputs) > 0

    def add_output(self, output_id, output):
        self.outputs[output_id] = output
        
    def add_motion_output(self, motion_output_id, motion_output):
        self.motion_outputs[motion_output_id] = motion_output

    def remove_output(self, output_id):
        del self.outputs[output_id]
        
    def remove_motion_output(self, motion_output_id):
        del self.motion_outputs[motion_output_id]

    def _work(self, content, type = "w"):
        workers = []
        outputs = self.outputs if type == "w" else self.motion_outputs
        for _, output in outputs.items():
            t = Thread(target = output.write if type == "w" else output.analyse, args = (content,))
            t.start()
            workers.append(t)
            
        for worker in workers:
            worker.join()

    def analyse(self, motion_vectors):
        self._work(motion_vectors, "a")

    def write(self, buffer):
        self._work(buffer, "w")