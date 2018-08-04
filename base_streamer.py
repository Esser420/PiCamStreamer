"""
BaseStreamer is the base class for generic streamer implementations.
"""
from utils.output_holder import OutputHolder
from threading import Thread

class BaseStreamer:
    def __init__(self, camera, port, format, resize, options):
        self.camera = camera
        self.port = port
        self.format = format
        self.resize = resize
        self.output = OutputHolder()
        self.sub_output = None
        self.options = options
        self.runner_thread = None
        self.ready_to_stop = False

    def close(self):
        self.camera.stop_recording(splitter_port = self.port)

    def stop(self, wait = True):
        if self.ready_to_stop:
            return

        self.ready_to_stop = True
        if wait:
            self.runner_thread.join()
        self.teardown_streamer()
        self.close()

    def start(self):
        self.setup_streamer()
        self.runner_thread = Thread(target = self.run_streamer)
        self.runner_thread.start()

    def run_streamer(self):
        output = self.sub_output if self.sub_output else self.output
        self.camera.start_recording(output, motion_output = self.output, format = self.format, splitter_port = self.port, **self.options)
        while not self.ready_to_stop:
            self.camera.wait_recording(1, self.port)

    def rebind_output(self, output):
        self.output = output
        if self.runner_thread:
            self.camera.split_recording(output)

    def setup_streamer(self):
        pass

    def teardown_streamer(self):
        pass
